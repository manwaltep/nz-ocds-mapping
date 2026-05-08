# Data quality findings

Issues discovered in MBIE's published GETS data while building this implementation. These are not pipeline bugs — they're problems in the source data that an OCDS publication would need to either work around, fix at source, or honestly disclose.

## Finding 1 — NZBN precision destroyed by scientific notation

**Severity:** High. ~4,000 distinct businesses cannot be uniquely identified.

**Where:** `GETS_supplier_data` and `GETS_supplier_data_historic`, column `Supplier_NZBN`.

### What we found

Querying the unique values of `Supplier_NZBN` across the full supplier dataset:

| Value | Rows | Distinct businesses |
|---|---|---|
| `9.43E+12` | **10,369** | **4,090** |
| `9.43E+11` | 24 | 12 |
| `""` (empty) | 7,091 | 2,817 |
| `NULL` | 3,382 | 2,833 |
| `GobleBuildingandDecoratingLtd` | 21 | 1 |
| `144659`, `M692320`, `3671051`, etc. | various | 1 each |

A New Zealand Business Number is a 13-digit integer (e.g. `9429045123456`). Every NZ NZBN starting with `943...` was at some point read as a number, auto-formatted as scientific notation by Excel (`9.43E+12`), and then exported back to CSV as the formatted display string — losing the trailing 11 digits permanently.

The result: in MBIE's own published procurement record, **4,090 distinct supplier businesses all share the same identifier `9.43E+12`.** That makes it impossible to:

- Deduplicate suppliers across tenders without resorting to fuzzy name matching
- Link suppliers to their NZBN registry record
- Aggregate procurement spend per business
- Detect when the same supplier wins multiple contracts under slight name variations

A handful of additional rows have a business name in the NZBN field (e.g. `Tend2CreateLtd`, `GobleBuildingandDecoratingLtd`), suggesting someone manually copied the wrong column during ingestion.

### Where the corruption happened

Both `GETS_supplier_data` and `GETS_supplier_data_historic` are typed `Supplier_NZBN: STRING` in Foundry. The corruption pre-dates Foundry ingestion. Most likely:

1. MBIE exports supplier data from their internal CMS to CSV
2. The CSV is opened in Excel for QA / formatting
3. Excel reads `Supplier_NZBN` as a number (it looks numeric), auto-formats as scientific notation (`9.43E+12`)
4. Re-exported as CSV, the formatted display string `"9.43E+12"` is what's written, not the underlying value
5. That CSV is what's published and what we ingested

This is a known Excel hazard and is the reason data publication best practice is to never round-trip identifier fields through Excel.

### Implications for the OCDS feed

We don't emit `identifier.id` values that fail format validation. Suppliers with destroyed NZBNs get a deterministic synthetic id (`supplier-{ocid}-{i}`) and no `identifier` block, rather than a fake "real" identifier shared across thousands of businesses. See `validate-nzbn` patch in the emitter (transform repo, May 2026).

### What would actually fix it

- **Re-ingest from MBIE's source system** with `Supplier_NZBN` explicitly typed as text/string at every step — never round-tripped through Excel.
- **Lookup remediation**: match `Business_Name` against the public NZBN registry (`api.business.govt.nz`) to recover the actual NZBN per supplier. Possible but requires permission and rate-limited bulk queries.

This is a finding worth raising with MBIE / NZGP. It's not unique to OCDS — it affects any analytical use of GETS supplier data — but OCDS publication is the lens that surfaces it most clearly.

---

## Finding 2 — Multi-office suppliers collapsed by name-only deduplication

**Severity:** Medium. Affects supplier counts on panel awards.

**Where:** Originally introduced by `Collect distinct array(business_name)` in the Pipeline Builder aggregation; mitigation in the emitter would still understate uniqueness because the underlying NZBNs are corrupted (Finding 1).

### What we found

OCID `ocds-nz-gets-28888398` (Christchurch City Council "3W Project Delivery Panel"):

- Source GETS data: **16 supplier rows**
- Spine output: **15 distinct supplier names**

The missing one: AECOM NEW ZEALAND LIMITED appears twice in the source — once at Cashel Street (Christchurch) and once at Mahuhu Crescent (Auckland). Both offices are legitimately on the panel. `Collect distinct array(business_name)` collapsed them into a single entry.

### Why this is hard to fix correctly

The right deduplication key would be `(NZBN, Business_Name, Full_Address)`. But:

- `NZBN` is corrupted for ~4,000 businesses (Finding 1)
- `Business_Name` is an exact-match key but doesn't distinguish offices of the same business
- `Full_Address` distinguishes offices but is free-text and inconsistent

So any deduplication rule will under- or over-count somewhere.

### Mitigation

In the Pipeline Builder aggregation, `Collect distinct array` could be replaced with `Collect array` to preserve every source row. Downstream code (the OCDS emitter) can then decide on a deduplication strategy that's appropriate for each consumer use case.

---

## Finding 3 — Award amounts often null on panel-style awards

**Severity:** Low. Reflects a real data structure decision in GETS, not a bug.

**Where:** `Awarded_Amount` column on award notices.

### What we found

Many awarded contracts (especially panels and pre-qualified supplier lists) have `Awarded_Amount: 0` or null. This isn't an error — at the panel formation point, no specific contract value has been agreed yet; specific values are agreed at later call-off stages that aren't published to GETS.

### Implications for OCDS

This is properly OCDS-modelled: if there's no agreed value, omit `awards[].value.amount`. The pipeline does this. The omission tells consumers what's true ("we have an award but no published value"), which is more honest than imputing a zero.

But it also means that **OCDS aggregation of NZ procurement spend will systematically under-count panel and call-off contracts** until contract management data starts flowing (Rule 34 mandates the data to exist; it's just not centrally published — see "Honest gaps" in the methodology).

---

## Finding 4 — Award outcomes recorded in unstructured `Comments` field

**Severity:** High. The actual awardees of many contracts are not in the structured supplier data.

**Where:** `GETS_award_notices.Comments` column (free text).

### What we found

While investigating OCID `ocds-nz-gets-28888398` (Christchurch City Council "3W Project Delivery Panel"), we noticed the GETS public web page lists 16 panel members in a structured "This tender has been awarded" section *plus* a separate free-text section titled **"Further Award Information: Contracts were awarded to:"** with **18 supplier names**. Four of those 18 names are not in the structured `GETS_supplier_data` table for that RFx:

- `Project Max`
- `Ako Engineers`
- `Lucas Haining` (the supplier exists in `GETS_supplier_data` for *other* RFx_IDs, just not 28888398)
- `Pinnacles Civil` (similar — exists for other RFx_IDs)

Querying the source: the entire free-text content is stored in `GETS_award_notices.Comments` for that RFx, exactly as displayed on the website.

### Format variation by agency

Sampling 15+ different agencies' Comments fields surfaced at least six distinct formats:

| Format | Example | Parseability |
|---|---|---|
| **DOC structured template** | `Successful supplier's name: Mainland Vector Contracting Ltd / Successful supplier's NZBN: 9429032195583 / Successful supplier's address: ...` | ★★★★★ Highest — labelled fields, includes uncorrupted 13-digit NZBNs |
| **Education Payroll inline** | `awarded to Dayforce New Zealand Limited (NZBN 942903980691)` | ★★★★ High — fixed pattern, NZBN inline |
| **NZTA single-line** | `Tonkin & Taylor was awarded to this contract for a total value $168,000.00` | ★★★ Medium — simple regex |
| **Generic single-supplier** | `Contract for D365 Development Squad awarded to Capgemini Limited` | ★★★ Medium |
| **Free-form multi-supplier list** | `Contracts were awarded to:  AECOM New Zealand Limited Benmore Mel Engineering Consultants Stantec  TSA Riley...` | ★★ Low — no clear delimiters between names |
| **Value bands only** | `Contract length = 1 year Contract value = $100,000 - $150,000` | n/a — no awardee info |

### A particularly important sub-finding: the `Comments` field can recover corrupted NZBNs

For Department of Conservation contracts, the `Comments` field contains **clean 13-digit NZBNs** in the form `Successful supplier's NZBN: 9429032195583`, while the structured `Supplier_NZBN` column for the same contract typically reads `9.43E+12` (see Finding 1).

So the prose form of the data is, in this respect, **higher quality than the structured form** — it preserves precision that the structured-data publication pipeline destroys. A Comments parser can recover real NZBNs that no longer exist in the structured table.

### Internal inconsistency: `Award_Type = "Not Awarded"` on awarded contracts

Across the entire sample we examined, the `Award_Type` column reads `"Not Awarded"` even on contracts that the Comments field clearly describes as awarded (often with named recipients and specific dollar amounts). The column appears to default to `"Not Awarded"` and is not consistently updated by agencies. **Consumers cannot rely on `Award_Type` alone to filter for awarded contracts.**

### Implications for OCDS

- A pipeline reading only structured fields **systematically under-reports awardees** for any contract whose award narrative lives in `Comments` and adds names beyond what's in `supplier_data`.
- The Comments field is, for a meaningful subset of agencies, the **authoritative awardee source** — and parseable with reasonable confidence.
- A parser-augmented OCDS feed materially improves downstream coverage. It also gives consumers an honest signal — `"this awardee was extracted from a free-text narrative, not a structured field"` — that lets them weight the data appropriately.

### Mitigation in this implementation

A separate Python transform (`comments_parser.py`, planned) will extract awardees from `GETS_award_notices.Comments` using format-specific regexes with confidence scores, and emit a side dataset (`gets_award_comments_parsed`) that the OCDS emitter can join in to enrich `awards[].suppliers[]`.

---

## Finding 5 — `Supplier_NZBN` table semantics inconsistent across tenders

**Severity:** High. The same column means different things on different rows.

**Where:** `GETS_supplier_data` and `GETS_supplier_data_historic`.

### What we found

Cross-referencing the structured `GETS_supplier_data` table against the awardees named in `Comments` across multiple RFx_IDs surfaces **inconsistent semantics**:

- **For RFx 24235499** (CCC "Pavement and Utilities Investigations Panel"), `GETS_supplier_data` has exactly 3 rows — `CORDE LIMITED`, `LUCAS HAINING LIMITED`, `The Isaac Construction Co Ltd` — and the Comments narrative says *"This contract has been awarded to CORDE Limited, Isaac Construction Limited and Lucas Haining Limited."* **Structured data = awardees. Consistent.**

- **For RFx 28888398** (CCC "3W Project Delivery Panel"), `GETS_supplier_data` has 16 rows and the Comments narrative names 18 awardees — with 4 names absent from `supplier_data`, 1 row in `supplier_data` (Pinnacles Civil Group Limited per the website Section 1) absent from our extract, and a duplicate AECOM entry that doesn't match what the website displays. **Structured data ≠ Comments awardees.**

There is **no flag** in the structured schema indicating which interpretation applies to a given row. The column could be representing:

- Actual awardees (RFx 24235499 case)
- Pre-qualified panel members eligible to bid (RFx 28888398 case — likely)
- Bidders who submitted responses (other cases — possibly)

### Implications for OCDS

The OCDS schema distinguishes:

- `tender.tenderers[]` — entities who responded to the tender
- `awards[].suppliers[]` — entities who actually won

Without knowing which of these `Supplier_NZBN` represents on a given row, **a literal mapping puts the wrong data in the wrong OCDS field roughly half the time**. Cross-referencing against `Comments` (Finding 4) is the only way to disambiguate from the publicly-available data.

### Mitigation

The forthcoming `comments_parser.py` transform will surface a `confidence` column on each parsed awardee, and the OCDS emitter will treat:

- `supplier_data` ∩ Comments-extracted = **awardee** → `awards[].suppliers[]`
- `supplier_data` only (no Comments mention) = **probable bidder** → `tender.tenderers[]` (or held back with a quality flag)
- Comments only (no `supplier_data` row) = **awardee with no structured record** → `awards[].suppliers[]` with `name` populated, no identifier, sourced flag

This won't be perfect (some agencies won't have parseable Comments at all), but it converts an unsignalled inconsistency into an explicit quality gradient.
