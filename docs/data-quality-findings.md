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
