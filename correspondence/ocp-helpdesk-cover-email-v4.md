# OCP Helpdesk cover email — v4 DRAFT

**To:** helpdesk@open-contracting.org
**From:** Manaaki Walker-Tepania, Project Unify
**Subject:** Working OCDS pipeline for NZ government procurement — request for review and prefix registration

---

Kia ora,

I'm writing on behalf of **Project Unify**, a New Zealand procurement intelligence implementation built on Palantir Foundry. We're publishing this email with two specific asks and a substantial body of evidence behind them.

**As of this week, we have a working pipeline that produces structurally valid OCDS 1.1.5 release JSON for ~28,000 awarded New Zealand government contracts back to 2015.** A sample release passed the OCDS Data Review Tool's structural checks; screenshot attached. The pipeline reads from publicly available GETS data, applies the mapping documented in the attached spreadsheet, and emits one OCDS release per OCID. Source code and the v0.4 mapping are open at [github.com/manwaltep/nz-ocds-mapping](https://github.com/manwaltep/nz-ocds-mapping).

This is the substantive answer to NZ's OGP commitment **NZ0029** — *Improve Government Procurement Transparency.* The IRM midterm review notes "specification of new mandatory fields for disclosure have yet to be determined," and Transparency International NZ has commented that "there has been no significant improvement" four years into the commitment. The underlying argument of this work is that the determination has effectively already been made — by the NZ Government Procurement Rules (5th edition, 2025) themselves — and that an OCDS publication can be stood up now, well ahead of the 2030 timeline, against data the Rules already mandate to exist.

We'd like OCP to review the mapping and the sample output before we engage MBIE / NZGP or publish more broadly. In particular we have **two specific asks** and seven points where independent technical view would strengthen the work.

## Two specific asks

1. **Prefix registration.** The DRT flags our OCID prefix `ocds-nz-gets-` as unregistered. We'd like to formally register it. What's the process, is `ocds-nz-gets` available, and what publisher metadata do you need from us?

2. **Mapping review.** The attached `ocds-nz-mapping-v0.4.xlsx` represents the implementation profile we'd like reviewed. Specific questions are listed under "Points for review" below.

## What I'm sharing

**1. Working pipeline evidence**
- DRT screenshot showing structural pass against `OCDS release package schema version 1.1` for a sample release
- Sample release JSON (an MBIE Economic Evaluation Panel award with 5 suppliers, OCID `ocds-nz-gets-11062705`)
- Public GitHub repo with the mapping, methodology, and changelog

**2. `ocds-nz-mapping-v0.4.xlsx`** — eight sheets:

1. **README** — methodology, sources, change log (v0.1 → v0.4)
2. **OCDS Mapping** — 114 OCDS 1.1.5 paths cross-referenced against GETS data, the NZ Government Procurement Rules (5th edition, 2025), and the NZGP Approved Government Model Templates. Status-coded: Direct / Derived / Vocab Translation / Constant / NZ Extension / Template-sourced / Rule-mandated / Gap.
3. **Vocab Translations** — 47 codelist translations between GETS values and OCDS controlled lists, each linked to the authoritative codelist file in `open-contracting/standard 1.2-dev` on GitHub.
4. **NZ Extensions** — **18 proposed extensions**, each anchored to a specific NZ Procurement Rule and (where applicable) a glossary citation rather than a vendor preference.
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

1. **OCID prefix.** Covered in "Two specific asks" above. NSW Treasury's publication uses `ocds-43qwtd-PP-{UUID}` with a registered prefix; we've drafted `ocds-nz-gets-{rfxId}` as the deterministic OCID (e.g. `ocds-nz-gets-32705858`) for stability across the multi-stage tender lifecycle. Happy to follow your guidance on the prefix string itself.

2. **Multi-stage procurement modelling.** Rule 10 explicitly recognises multi-step processes (ROI followed by RFP/RFT) — and the glossary defines ROI as *"the first formal stage of a multistep tender process."* I've drafted modelling these as **one OCID with stage transitions via release tags** over time (Stage 1 = `['tender']` with `procurementMethod=selective`, Stage 2 = `['tenderUpdate']` or `['tenderAmendment']`, Award stage = `['award']`). In NZ practice, GETS sometimes assigns the same RFx_ID across both phases and sometimes different ones. How have other implementations handled this ambiguity?

3. **Procurement method mapping.** `tender.procurementMethod` derives from GETS `Competition_Type` (the primary signal), and `tender.procurementMethodDetails` carries the GETS `RFx_Type` as free text:
   - Competition_Type='Open Competition' (any RFx_Type) → `open`
   - Multi-step ROI → RFP/RFT → `selective`
   - Closed Competition from Pre-qualified Suppliers (Rule 22/23) → `selective`
   - Closed Competition with Rule 12 exemption → `limited`
   - Award Notice with Rule 12 single-supplier exemption → `direct`
   The pipeline implements this and emits valid `procurementMethod` codelist values. Defensible? Or is there a cleaner convention?

4. **Release tag strategy.** GETS award notices carry both tender data and award data. We emit them as releases with `tag=['award']` for awarded, `['awardCancellation']` for not-awarded, with separate `['tender']` releases for current open tenders from the GETS RSS feed. Future Procurement Opportunities (Rule 37, defined as a *"rolling list covering at least the next 12 months"*) → `['planning']`. Consistent with OCP guidance?

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

   The pipeline currently carries `agencyTier` and `abbreviation` on `parties[].details` as the seeds of `nz-agency-tier`. The DRT correctly flags these as not-in-standard. Once we have a registered prefix and your view on the extension proposals, we'll formalise schemas in the [extensions registry](https://github.com/open-contracting-extensions) format.

6. **OCDS version target.** We've targeted 1.1.5 (current stable, used by NSW Treasury) for v1 with a migration path to 1.2 once stabilised. The Vocab Translations sheet in v0.4 already references 1.2-dev codelist files for forward compatibility. Reasonable strategy?

7. **Honest gaps declaration.** Three OCDS sections are largely unrecoverable from current GETS data:
   - **Planning** — partially mandated by Rule 6 (12 elements) + Rule 7 (estimated value) + Rule 37 (FPOs) to exist in agency procurement plans, but not publicly published
   - **Contract performance / implementation** — mandated by Rules 34 (9 CMS fields) and 35 (KPIs) to exist in agency contract management systems, but not centralised
   - **Bids** — Rule 5 protects bid content as commercial-in-confidence
   These are publication gaps, not data gaps — the data exists by law but isn't structured for output. Is this the right way to declare partial-publication gaps in OCDS?

## Context that might help

- The pipeline runs on Palantir Foundry with full visual lineage from any OCDS output field back to its GETS source. That's the probity story we'll lead with when we engage MBIE / NZGP.
- We're operating outside government as a small civil-society-aligned implementation team (currently solo). This is genuinely independent work, not vendor-positioned.
- Sequence: OCP Helpdesk technical review (this email) → Transparency International NZ + academic/journalist engagement → MBIE / NZGP outreach with a working prototype + external endorsements.
- We're aware of and have studied NSW Treasury's OCDS publication on the OCP Data Registry. The "no longer updated by the publisher" status and undocumented-additional-fields situation is instructive — Foundry's automated pipeline + branched ontology + downstream `ocdskit` validation step is intended to prevent the same drift mode.
- The full NZ Government Procurement Rules glossary has been mined for terminology and structural definitions. Each NZ extension cites the relevant glossary entry where applicable, which strengthens the legitimacy argument when this work is shared with MBIE/NZGP.

A 30-minute video call would be ideal but not essential. Written feedback on the spreadsheet and sample release would be enormously helpful — particularly on the seven points above. We can share read access to the working Foundry pipeline if that would be useful, and source code is on GitHub now.

Ngā mihi nui,

Manaaki Walker-Tepania
Project Unify
[contact details]

---

## Attachments

1. `ocds-nz-mapping-v0.4.xlsx` (primary mapping)
2. `sample-release-ocds-nz-gets-11062705.json` (working pipeline output, DRT-validated)
3. `drt-structural-pass-screenshot.png` (DRT confirming structural compliance)
4. (optional) Project Unify one-pager with the NZ0029 framing

---

## Notes for the sender (not part of the email)

**v4 changes from v3:**
- **Subject line repositioned** — "Working OCDS pipeline for NZ government procurement — request for review and prefix registration." Stronger lead than "Request for review."
- **Opening reframed** — leads with the working pipeline as fait accompli, then connects to NZ0029. v3 led with the proposal narrative.
- **Two specific asks now in their own section** at the top — prefix registration + mapping review. Easier for the helpdesk to action.
- **References v0.4 spreadsheet** with 114 paths (was v0.3 with 91)
- **Pipeline evidence** elevated to its own attachment category — DRT screenshot, sample release JSON, GitHub repo
- **Question 5 epilogue** added — explains that `agencyTier` and `abbreviation` are intentional non-standard fields that DRT correctly flags, and we'll formalise as extensions once we have prefix + OCP review
- **GitHub repo URL** added (was implied in v3)
- Length reduced where possible — 7 questions still present but tighter

**Carry-forward notes from v3:**
- Lead with the Rules-OCDS link
- NSW failure mode acknowledged respectfully
- Civil society framing invokes IRM's "systematically included" language
- Reasonable expectations on response time — OCP Helpdesk typically responds in 1–3 weeks
- Strip these notes before sending; fill in your contact details
- Save DRT screenshot from your Chrome tab before sending
- Save sample release JSON to a file (the MBIE Economic Evaluation Panel one we validated)
