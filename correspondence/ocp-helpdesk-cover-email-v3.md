# OCP Helpdesk cover email — v3 DRAFT

**To:** helpdesk@open-contracting.org
**From:** Manaaki Walker-Tepania, Project Unify
**Subject:** Request for review — draft NZ-OCDS implementation against GETS data

---

Kia ora,

I'm working on **Project Unify**, a New Zealand procurement intelligence platform built on Palantir Foundry. We're producing a working OCDS-compliant feed against the publicly available NZ Government Electronic Tenders Service (GETS) data, with the aim of helping deliver against NZ's OGP commitment **NZ0029** — *Improve Government Procurement Transparency* — substantially ahead of its current 2030 implementation timeline.

NZ0029 explicitly commits to OCDS alignment, but the IRM midterm review notes "specification of new mandatory fields for disclosure have yet to be determined." Civil society — Transparency International NZ has published critical commentary that "there has been no significant improvement" after four years of government commitments. The OGP-IRM review explicitly recommends that civil society participation be "systematically included" in oversight; this engagement is part of that.

I'd like Project Unify's draft mapping to be reviewed by OCP before we ship it to MBIE / NZGP or publish it openly.

## What I'm sharing

Attached: **`ocds-nz-mapping-v0.3.xlsx`** — a draft NZ-OCDS implementation profile with eight sheets:

1. **README** — methodology, sources, change log (v0.1 → v0.2 → v0.3)
2. **OCDS Mapping** — 91 OCDS 1.1.5 paths cross-referenced against GETS data, the NZ Government Procurement Rules (5th edition, 2025), and the NZGP Approved Government Model Templates. Status-coded: Direct / Derived / Vocab Translation / Constant / NZ Extension / Template-sourced / Rule-mandated / Gap.
3. **Vocab Translations** — 47 codelist translations between GETS values and OCDS controlled lists, each linked to the authoritative codelist file in `open-contracting/standard 1.2-dev` on GitHub.
4. **NZ Extensions** — **18 proposed extensions**, each anchored to a specific NZ Procurement Rule and (where applicable) a glossary citation rather than a vendor preference.
5. **Rules Inventory** — all 47 NZ Procurement Rules with OCDS-relevance commentary.
6. **Templates Inventory** — 31 NZGP A-GMTs with OCDS-relevance commentary.
7. **Publishing Governance** — 8-step publishing process and 8 roles, adapted from NSW Government Open Data Publishing Guidelines V3.0 (Nov 2022) with NZ localisation (OIA in place of GIPA Act).
8. **Sensitivity Classification** — 14-row field-level publish/redact/aggregate/suppress policy anchored to NZGP Rule 5, OIA 1982 s9, Privacy Act 2020, and NSW Information Classification Labelling and Handling Guidelines V2.3.

## The core finding

The mapping work surfaced an insight I haven't seen named publicly elsewhere: **the NZ Government Procurement Rules already mandate the data OCDS expects.** Of 91 OCDS paths analysed:

- 23 Direct + 13 Derived = data flows from GETS today
- 19 Rule-mandated = required to exist by law (Rule 6's 12 planning elements, Rule 32's 10 contract-award fields, Rule 34's 9 CMS fields, Rule 35's contract-management plan KPIs, Rule 36's quarterly prompt-payment publication, Rule 37's Future Procurement Opportunities)
- 14 Template-sourced = captured in mandatory NZGP Approved Government Model Templates but not centrally published
- 18 NZ Extension proposals (each Rule + glossary anchored)
- Small remainder of constants, vocab translations, and genuine gaps

So **80%+ of OCDS coverage closes by structuring data the Rules already require.** OCDS-NZ alignment is therefore not a new data-collection burden on agencies — it's a structured-publication layer over data the Rules already mandate to exist.

A specific finding worth flagging: **Rule 32 mandates 10 fields in a contract award notice, but the GETS schema captures only six of them.** That's an internal compliance gap inside MBIE's own system, surfaced from MBIE's own published Rules.

## Specific things I'd value your review on

1. **OCID prefix.** I've drafted `ocds-nz-gets-{rfxId}` as the deterministic OCID (e.g. `ocds-nz-gets-32705858`). NSW Treasury's publication uses `ocds-43qwtd-PP-{UUID}` with a registered prefix. Should we apply for a registered prefix, and what does that process look like? Is `nz-gets` available, or would you assign something else?

2. **Multi-stage procurement modelling.** Rule 10 explicitly recognises multi-step processes (ROI followed by RFP/RFT) — and the glossary defines ROI as *"the first formal stage of a multistep tender process."* I've drafted modelling these as **one OCID with stage transitions via release tags** over time (Stage 1 = `['tender']` with `procurementMethod=selective`, Stage 2 = `['tenderUpdate']` or `['tenderAmendment']`, Award stage = `['award']`). In NZ practice, GETS sometimes assigns the same RFx_ID across both phases and sometimes different ones. How have other implementations handled this ambiguity?

3. **Procurement method mapping (refined per practitioner feedback).** Going by the structure I've drafted: `tender.procurementMethod` derives from GETS `Competition_Type` (the primary signal), and `tender.procurementMethodDetails` carries the GETS `RFx_Type` as free text. So:
   - Competition_Type='Open Competition' (any RFx_Type) → `open`
   - Multi-step ROI → RFP/RFT → `selective`
   - Closed Competition from Pre-qualified Suppliers (Rule 22/23) → `selective`
   - Closed Competition with Rule 12 exemption → `limited`
   - Award Notice with Rule 12 single-supplier exemption → `direct`
   Defensible? Or is there a clearer convention?

4. **Release tag strategy.** GETS award notices carry both tender data and award data. I've proposed emitting them as releases with `tags=['award']` for awarded, `['awardCancellation']` for not-awarded, with separate `['tender']` releases for current open tenders from the RSS feed. Future Procurement Opportunities (Rule 37, defined as a *"rolling list covering at least the next 12 months"*) → `['planning']`. Consistent with OCP guidance?

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

6. **OCDS version target.** Should we target 1.1.5 (current stable, used by NSW Treasury) or 1.2-dev (upcoming, more codelist values)? My instinct is 1.1.5 for v1 with a migration path to 1.2 once stabilised. The Vocab Translations sheet in v0.3 already references 1.2-dev codelist files for forward compatibility.

7. **Honest gaps declaration.** I've flagged three OCDS sections as largely unrecoverable from current GETS data:
   - **Planning** — partially mandated by Rule 6 (12 elements) + Rule 7 (estimated value) + Rule 37 (FPOs) to exist in agency procurement plans, but not publicly published
   - **Contract performance / implementation** — mandated by Rules 34 (9 CMS fields) and 35 (KPIs) to exist in agency contract management systems, but not centralised
   - **Bids** — Rule 5 protects bid content as commercial-in-confidence
   These are publication gaps not data gaps — the data exists by law but isn't structured for output. Is this the right way to declare partial-publication gaps in OCDS?

## Context that might help

- We have a working Pipeline Builder pipeline in development that produces OCDS-shaped output from GETS source data with full visual lineage. Foundry's lineage UI gives us a clickable trail from any output field back to source — that's the probity story we want to lead with when we engage MBIE / NZGP.
- We're operating outside government as a small civil-society-aligned implementation team (currently solo). This is genuinely independent work, not vendor-positioned.
- We haven't approached MBIE / NZGP yet. Sequence is: OCP Helpdesk technical review → Transparency NZ + academic/journalist engagement → MBIE / NZGP outreach with a working prototype + external endorsements.
- We're aware of and have studied NSW Treasury's OCDS publication on the OCP Data Registry. The "no longer updated by the publisher" status and undocumented-additional-fields situation is informative — Foundry's automated pipeline + branched ontology + integrated `ocdskit` validation should prevent the same drift mode.
- We've also reviewed NSW Government's open-data publishing process and information classification guidelines as governance reference material; both are reflected in the Publishing Governance and Sensitivity Classification sheets.
- The full NZ Government Procurement Rules glossary has been mined for terminology and structural definitions. Each NZ extension cites the relevant glossary entry where applicable, which strengthens the legitimacy argument when this work is shared with MBIE/NZGP.

A 30-minute video call would be ideal but not essential. Written feedback on the spreadsheet would also be enormously helpful — particularly on the seven questions above. Happy to share the working Pipeline Builder build once it's in a reviewable state.

Ngā mihi nui,

Manaaki Walker-Tepania
Project Unify
[contact details]

---

## Attachments

- `ocds-nz-mapping-v0.3.xlsx` (primary)
- (optional) Project Unify one-pager with the NZ0029 framing

---

## Notes for the sender (not part of the email)

**v3 changes from v2:**
- References v0.3 spreadsheet (was v0.2)
- 18 extensions (was 14) — surfaces 4 new extensions from glossary mining: `nz-treaty-of-waitangi-exception`, `nz-procurement-method-detail`, `nz-contracting-model`, `nz-secondary-procurement`
- 47 vocab translations (was 38) — added 9 new entries from glossary review and procurement-method refinement
- **NEW question 2**: explicit multi-stage modelling question (ROI → RFP/RFT) — this came up in the Pipeline Builder design discussion and is a real ambiguity worth OCP's view
- **Refined question 3**: procurement method mapping now reflects practitioner feedback (Competition_Type primary, RFx_Type as details). Cleaner mapping.
- **Question 5** now lists 9 specific extensions with glossary anchors — stronger argument that these aren't vendor-invented
- **Question 7** now distinguishes "publication gaps" from "data gaps" — clearer ask of OCP about how to declare these
- Adds a paragraph in "context" about glossary mining — signals depth of the work without making the email longer

**Other notes for the sender (carry forward from v2):**
- Subject line is specific ("draft NZ-OCDS implementation against GETS data")
- Lead with the Rules-OCDS link
- Working pipeline is mentioned (concrete, not just spec)
- NSW failure mode acknowledged respectfully
- Civil society framing invokes IRM's "systematically included" language
- Reasonable expectations on response time — OCP Helpdesk typically responds in 1–3 weeks
- Strip these notes before sending; fill in your contact details
