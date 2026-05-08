# OCP Helpdesk cover email — v6 FINAL (sender's version)

**To:** helpdesk@open-contracting.org
**From:** Manaaki Walker-Tepania
**Subject:** Independent research — NZ-OCDS implementation profile and working pipeline; request for review and prefix registration

---

Hello,

I'm writing as an independent researcher conducting an implementation project on what an OCDS-aligned publication of New Zealand government procurement data could look like in practice. The work is not affiliated with any government agency, vendor, or institution — it's a civil-society-oriented research project examining whether NZ's OGP commitment **NZ0029** (*Improve Government Procurement Transparency*) can be substantively delivered against publicly available data, noting full delivery is expected by 2030.

The output is two-fold:

1. A **draft NZ-OCDS implementation profile** mapping all 47 NZ Government Procurement Rules (5th edition, 2025) and the GETS data schema against OCDS 1.1.5. Documented at [github.com/manwaltep/nz-ocds-mapping](https://github.com/manwaltep/nz-ocds-mapping); current version is v0.4.

2. A **working pipeline** that, as of this week, produces structurally valid OCDS 1.1.5 release JSON for ~28,000 awarded NZ government contracts back to 2015. A sample release passed the OCDS Data Review Tool's structural checks; screenshot attached, JSON sample also attached.

I'd like OCP's technical review on the mapping and the sample output before moving forward. Specifically, I have **two practical asks** and seven points where independent technical view would strengthen the work.

## Two practical asks

1. **Prefix registration.** The DRT flags the OCID prefix `ocds-nz-gets-` as unregistered. Is there a current formally registered OCID prefix otherwise could I register this one. What's the process, is `ocds-nz-gets` available, and what publisher metadata is required?

2. **Mapping review.** The attached `ocds-nz-mapping-v0.4.xlsx` represents the implementation profile I'd value review on. Specific questions are listed under "Points for review" below.

## What I'm sharing

**1. Working pipeline evidence**
- DRT screenshot showing structural pass against the `OCDS release package schema version 1.1` for a sample release
- Sample release JSON (an MBIE Economic Evaluation Panel award with 5 suppliers, OCID `ocds-nz-gets-11062705`)
- Public GitHub repo with the mapping, methodology, and changelog

**2. `ocds-nz-mapping-v0.4.xlsx`** — eight sheets:

1. **README** — methodology, sources, change log (v0.1 → v0.4)
2. **OCDS Mapping** — 114 OCDS 1.1.5 paths cross-referenced against GETS data, the NZ Government Procurement Rules (5th edition, 2025), and the NZGP Approved Government Model Templates. Status-coded: Direct / Derived / Vocab Translation / Constant / NZ Extension / Template-sourced / Rule-mandated / Gap.
3. **Vocab Translations** — 47 codelist translations between GETS values and OCDS controlled lists, each linked to the authoritative codelist file in `open-contracting/standard 1.2-dev` on GitHub.
4. **NZ Extensions** — **18 proposed extensions**, each anchored to a specific NZ Procurement Rule and (where applicable) a glossary citation rather than designer preference.
5. **Rules Inventory** — all 47 NZ Procurement Rules with OCDS-relevance commentary.
6. **Templates Inventory** — 31 NZGP A-GMTs with OCDS-relevance commentary.
7. **Publishing Governance** — 8-step publishing process and 8 roles, adapted from NSW Government Open Data Publishing Guidelines V3.0 (Nov 2022) with NZ localisation (OIA in place of GIPA Act).
8. **Sensitivity Classification** — 14-row field-level publish/redact/aggregate/suppress policy anchored to NZGP Rule 5, OIA 1982 s9, Privacy Act 2020, and NSW Information Classification Labelling and Handling Guidelines V2.3.

## The core finding

The mapping work surfaced an insight I haven't seen named publicly elsewhere: **the NZ Government Procurement Rules already mandate the data OCDS expects.** Of 114 OCDS paths analysed:

- ~32% Direct + Derived = data flows from GETS today
- ~17% Rule-mandated = required to exist by law (Rule 6's 12 planning elements, Rule 32's 10 contract-award fields, Rule 34's 9 CMS fields, Rule 35's contract-management plan KPIs, Rule 36's quarterly prompt-payment publication, Rule 37's Future Procurement Opportunities)
- ~12% Template-sourced = captured in mandatory NZGP Approved Government Model Templates but not centrally published
- ~27% NZ Extension proposals (each Rule + glossary anchored)
- The remainder split between constants, vocab translations, and genuine gaps

So **~80% of OCDS coverage closes by structuring data the Rules already require.** OCDS-NZ alignment is therefore not a new data-collection burden on agencies — it's a structured-publication layer over data the Rules already mandate to exist.

A specific finding worth flagging: **Rule 32 mandates 10 fields in a contract award notice, but the GETS schema captures only six of them.** That's an internal compliance gap inside MBIE's own system, surfaced from MBIE's own published Rules.

## Points for review

1. **OCID prefix.** Covered in "Two practical asks" above. NSW Treasury's publication uses `ocds-43qwtd-PP-{UUID}` with a registered prefix; I've drafted `ocds-nz-gets-{rfxId}` as the deterministic OCID (e.g. `ocds-nz-gets-32705858`) for stability across the multi-stage tender lifecycle. Happy to follow your guidance on the prefix string itself.

2. **Multi-stage procurement modelling.** Rule 10 explicitly recognises multi-step processes (ROI followed by RFP/RFT) — and the glossary defines ROI as *"the first formal stage of a multistep tender process."* I've drafted modelling these as **one OCID with stage transitions via release tags** over time (Stage 1 = `['tender']` with `procurementMethod=selective`, Stage 2 = `['tenderUpdate']` or `['tenderAmendment']`, Award stage = `['award']`). In NZ practice, GETS sometimes assigns the same RFx_ID across both phases and sometimes different ones. How have other implementations handled this ambiguity?

3. **Procurement method mapping.** `tender.procurementMethod` derives from GETS `Competition_Type` (the primary signal), and `tender.procurementMethodDetails` carries the GETS `RFx_Type` as free text:
   - Competition_Type='Open Competition' (any RFx_Type) → `open`
   - Multi-step ROI → RFP/RFT → `selective`
   - Closed Competition from Pre-qualified Suppliers (Rule 22/23) → `selective`
   - Closed Competition with Rule 12 exemption → `limited`
   - Award Notice with Rule 12 single-supplier exemption → `direct`

   The pipeline implements this and emits valid `procurementMethod` codelist values. Defensible? Or is there a cleaner convention?

4. **Release tag strategy.** GETS award notices carry both tender data and award data. Releases are emitted with `tag=['award']` for awarded, `['awardCancellation']` for not-awarded, with separate `['tender']` releases for current open tenders from the GETS RSS feed. Future Procurement Opportunities (Rule 37, defined as a *"rolling list covering at least the next 12 months"*) → `['planning']`. Consistent with OCP guidance?

5. **NZ extensions — 18 proposed.** Each anchored to Rules + glossary. Particularly value feedback on:
   - **`nz-treaty-of-waitangi-exception`** — formal Te Tiriti exception in NZ international trade agreements, distinct from Rule 11 opt-out and Rule 12 exemption. No equivalent I've seen in other jurisdictions.
   - **`nz-tender-coverage`** (AoG / Common Capability / Syndicated / Sole Agency / On-behalf — Rules 38, 39, 40, 22)
   - **`nz-economic-benefits`** with Trans-Tasman scope flag (Rule 8 mandates ≥10% evaluation weighting; the glossary explicitly says "New Zealand business" for Rule 8 *includes* Australian business)
   - **`nz-procurement-method-detail`** sub-typing the OCDS method codes (competitive-dialogue, lean-agile-procurement with Big Room Event, multi-step-roi-rfp etc.)
   - **`nz-contracting-model`** orthogonal to procurement method (outcomes-based-relational, commissioning, social-investment, lean-agile, collaborative)
   - **`nz-mandate-level`** (which tier of Rules compliance applies: mandated / expected / encouraged)
   - **`nz-prompt-payment`** (Rule 36 — already publicly reported quarterly; extension structures the existing data)
   - **`nz-te-reo-names`** (bilingual party names; Rule 1 / Te Tiriti o Waitangi anchor — MBIE's own GETS schema flags Te Reo macron rendering as broken at source)
   - **`nz-secondary-procurement`** (formal NZ term for panel call-offs — Rules 12, 22; glossary citation)

   The pipeline currently carries `agencyTier` and `abbreviation` on `parties[].details` as the seeds of `nz-agency-tier`. The DRT correctly flags these as not-in-standard. Once a registered prefix and your view on the extension proposals are in hand, I'll formalise schemas in the extensions registry format ([github.com/open-contracting-extensions](https://github.com/open-contracting-extensions)).

6. **OCDS version target.** I've targeted 1.1.5 (current stable, used by NSW Treasury) for v1 with a migration path to 1.2 once stabilised. The Vocab Translations sheet in v0.4 already references 1.2-dev codelist files for forward compatibility. Reasonable strategy?

7. **Honest gaps declaration.** Three OCDS sections are largely unrecoverable from current GETS data:
   - **Planning** — partially mandated by Rule 6 (12 elements) + Rule 7 (estimated value) + Rule 37 (FPOs) to exist in agency procurement plans, but not publicly published
   - **Contract performance / implementation** — mandated by Rules 34 (9 CMS fields) and 35 (KPIs) to exist in agency contract management systems, but not centralised
   - **Bids** — Rule 5 protects bid content as commercial-in-confidence

   These are publication gaps, not data gaps — the data exists by law but isn't structured for output. Is this the right way to declare partial-publication gaps in OCDS?

## Context that might help

- The work is **independent and unfunded**. I'm a solo researcher. There is no commercial interest behind this email, no vendor positioning, and no government affiliation.
- *Project Unify* — is the naming convention used in my folder structures — nothing else.
- The pipeline includes full output-to-source lineage — every OCDS field traces back to its specific GETS source column, so the provenance story is auditable end-to-end.
- Sequence: OCP Helpdesk technical review (this email) → Others (to be determined) → MBIE / NZGP outreach with a working prototype + external endorsements.
- I've studied NSW Treasury's OCDS publication on the OCP Data Registry. The "no longer updated by the publisher" status and undocumented-additional-fields situation is instructive — automated regeneration plus a downstream `ocdskit` validation step is intended to prevent the same drift mode.
- The full NZ Government Procurement Rules glossary has been mined for terminology and structural definitions. Each NZ extension cites the relevant glossary entry where applicable.

Written feedback on the spreadsheet and sample release would be enormously helpful — particularly on the seven points above. I'm happy to share further some details (where I can) of the pipeline implementation if that would aid review.

## Attachments

- `ocds-nz-mapping-v0.4.xlsx` (primary mapping) (attached for convenience)
- `sample-release-ocds-nz-gets-11062705.json` (working pipeline output, DRT-validated)
- `drt-structural-pass-screenshot.png` (DRT confirming structural compliance)

Regards,

Manaaki Walker-Tepania

---

## Notes for the record (not part of the email)

This is the **final sender's version** of the cover email, edited from v5 by the author before sending.

**v6 changes from v5:**
- Greeting changed to "Hello," (was "Kia ora")
- "implementation research" → "implementation project" in opening
- Reframed timeline as "noting full delivery is expected by 2030" (less promissory)
- Ask 1 now also asks whether NZ already has a registered prefix before requesting one
- Added a context bullet clarifying *Project Unify* is a folder-naming convention only — guards against future repo references being misread as branding
- Sequence updated: middle step is "Others (to be determined)" rather than naming Transparency NZ specifically — keeps options open
- Removed the "30-minute video call would be ideal" line
- "happy to share further details" → "happy to share further some details (where I can)" — lightly hedged
- Closing changed to "Regards," (was "Ngā mihi nui,")
- Extensions registry URL inlined in question 5 epilogue
