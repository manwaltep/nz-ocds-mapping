# OCP Helpdesk cover email — v2 DRAFT

**To:** helpdesk@open-contracting.org
**From:** Manaaki Walker-Tepania, Project Unify
**Subject:** Request for review — draft NZ-OCDS implementation against GETS data

---

Kia ora,

I'm working on **Project Unify**, a New Zealand procurement intelligence platform built on Palantir Foundry. We're producing a working OCDS-compliant feed against the publicly available NZ Government Electronic Tenders Service (GETS) data, with the aim of helping deliver against NZ's OGP commitment **NZ0029** — *Improve Government Procurement Transparency* — substantially ahead of its current 2030 implementation timeline.

NZ0029 explicitly commits to OCDS alignment, but the IRM midterm review notes "specification of new mandatory fields for disclosure have yet to be determined." Civil society — Transparency International NZ has published critical commentary that "there has been no significant improvement" after four years of government commitments. The OGP-IRM review explicitly recommends that civil society participation be "systematically included" in oversight; this engagement is part of that.

I'd like Project Unify's draft mapping to be reviewed by OCP before we ship it to MBIE / NZGP or publish it openly.

## What I'm sharing

Attached: **`ocds-nz-mapping-v0.2.xlsx`** — a draft NZ-OCDS implementation profile with eight sheets:

1. **README** — methodology, sources, change log
2. **OCDS Mapping** — 91 OCDS 1.1.5 paths cross-referenced against GETS data, the NZ Government Procurement Rules (5th edition, 2025), and the NZGP Approved Government Model Templates. Status-coded: Direct / Derived / Vocab Translation / Constant / NZ Extension / Template-sourced / Rule-mandated / Gap.
3. **Vocab Translations** — 38 codelist translations between GETS values and OCDS controlled lists, each linked to the authoritative codelist file in `open-contracting/standard 1.2-dev` on GitHub.
4. **NZ Extensions** — 14 proposed extensions, **each anchored to a specific NZ Procurement Rule** rather than a vendor preference.
5. **Rules Inventory** — all 47 NZ Procurement Rules with OCDS-relevance commentary.
6. **Templates Inventory** — 31 NZGP A-GMTs with OCDS-relevance commentary (procurement plans, RFx templates, Government Model Contracts, contract management plans).
7. **Publishing Governance** — 8-step publishing process and 8 roles, adapted from NSW Government Open Data Publishing Guidelines V3.0 (Nov 2022) with NZ localisation (OIA in place of GIPA Act).
8. **Sensitivity Classification** — 14-row field-level publish/redact/aggregate/suppress policy anchored to NZGP Rule 5 (Protection of supplier information), OIA 1982 s9, Privacy Act 2020, and NSW Information Classification Labelling and Handling Guidelines V2.3.

## The framing — and why I think it's significant

The core insight from the mapping work: **the NZ Government Procurement Rules already mandate the data OCDS expects.** Of 91 OCDS paths analysed:

- 23 Direct + 13 Derived = data flows from GETS today
- 19 Rule-mandated = required to exist by law (e.g. Rule 6's 12 planning elements, Rule 32's 10 contract-award fields, Rule 34's 9 Contract Management System fields, Rule 36's quarterly prompt-payment publication, Rule 37's Future Procurement Opportunities) but not currently published structurally
- 14 Template-sourced = captured in mandatory NZGP templates (A-GMTs) but not centrally published
- 14 NZ Extension proposals (each Rule-anchored)
- Small remainder of constants, vocab translations, and genuine gaps

So **80%+ of OCDS coverage closes by structuring data the Rules already require.** OCDS-NZ alignment is therefore not a new data-collection burden on agencies — it's a structured-publication layer over data the Rules already mandate to exist. To my knowledge, no public document has previously made this Rules-OCDS crosswalk explicit.

A specific finding worth flagging: **Rule 32 mandates 10 fields in a contract award notice, but the GETS schema captures only six of them.** That's an internal compliance gap inside MBIE's own system, surfaced from MBIE's own published Rules.

## Specific things I'd value your review on

1. **OCID prefix.** I've drafted `ocds-nz-gets-{rfxId}` as the deterministic OCID (e.g. `ocds-nz-gets-32705858`). NSW Treasury's publication uses `ocds-43qwtd-PP-{UUID}` with a registered prefix. Should we apply for a registered prefix (and what does that process look like)? Is `nz-gets` available, or would you assign something else?

2. **Procurement method mapping.** GETS RFx Type → OCDS `tender.procurementMethod`:
   - Request for Tenders (open competition) → `open`
   - Request for Proposals (open competition) → `selective`
   - Request for Quotations → `limited`
   - Closed competition (any RFx type) → `limited`
   Defensible, or is there a clearer convention in implementations you've seen?

3. **Release tag strategy.** GETS award notices carry both tender data and award data. I've proposed emitting them as releases with `tags=['award']` for awarded, `['awardCancellation']` for not-awarded, with separate `['tender']` releases for current open tenders from the RSS feed. Future Procurement Opportunities (Rule 37) → `['planning']`. Consistent with OCP guidance?

4. **NZ extensions.** 14 proposed extensions in the spreadsheet. I'd particularly value feedback on:
   - `nz-tender-coverage` (AoG / Common Capability / Syndicated / Sole Agency / On-behalf — sourced from Rules 38, 39, 40, 22)
   - `nz-economic-benefits` (Rule 8 mandates ≥10% evaluation weighting; seven benefit categories)
   - `nz-mandate-level` (which tier of Rules compliance applies to the agency: mandated / expected / encouraged)
   - `nz-prompt-payment` (Rule 36 — already publicly reported quarterly; extension structures the existing data)
   - `nz-te-reo-names` (bilingual party names; Rule 1 / Te Tiriti o Waitangi anchor, plus MBIE's own GETS schema flags Te Reo macron rendering as broken at source)

5. **OCDS version target.** Should we target 1.1.5 (current stable, used by NSW Treasury) or 1.2-dev (upcoming, more codelist values)? My instinct is 1.1.5 for v1 with a migration path to 1.2 once stabilised.

6. **Honest gaps declaration.** I've flagged three OCDS sections as largely unrecoverable from current GETS data:
   - **Planning** (179 fields) — partially mandated by Rule 6 to exist in agency procurement plans, but not publicly published
   - **Contract performance / implementation** (500+ fields) — mandated by Rules 34 & 35 to exist in agency CMS, but not centralised
   - **Bids** (60 fields) — Rule 5 protects bid content as commercial-in-confidence
   Is this the right way to declare partial-publication gaps? Are there OCDS conventions for "this stage is mandated to exist offline but isn't published" that I should adopt?

## Context that might help

- We have a working Pipeline Builder pipeline in development that produces OCDS-shaped output from GETS source data with full visual lineage. Foundry's lineage UI gives us a clickable trail from any output field back to source — that's the probity story we want to lead with when we engage MBIE / NZGP.
- We're operating outside government as a small civil-society-aligned implementation team (currently solo). This is genuinely independent work, not vendor-positioned.
- We haven't approached MBIE / NZGP yet. Sequence is: OCP Helpdesk technical review → Transparency NZ + academic/journalist engagement → MBIE / NZGP outreach with a working prototype + external endorsements.
- We're aware of and have studied NSW Treasury's OCDS publication on the OCP Data Registry. The "no longer updated by the publisher" status and undocumented-additional-fields situation is informative — Foundry's automated pipeline + branched ontology + integrated `ocdskit` validation should prevent the same drift mode.
- We've also reviewed NSW Government's open-data publishing process and information classification guidelines as governance reference material; both are reflected in the Publishing Governance and Sensitivity Classification sheets.

A 30-minute video call would be ideal but not essential. Written feedback on the spreadsheet would also be enormously helpful — particularly on the six questions above. Happy to share the working Pipeline Builder build once it's in a reviewable state.

Ngā mihi nui,

Manaaki Walker-Tepania
Project Unify
[contact details]

---

## Attachments

- `ocds-nz-mapping-v0.2.xlsx` (primary)
- (optional) Project Unify one-pager with the NZ0029 framing

---

## Notes for the sender (not part of the email)

- **Subject line is now more specific** ("draft NZ-OCDS implementation against GETS data" vs the v1 generic "request for review"). OCP Helpdesk receives many requests; specific subjects get prioritised.
- **Lead with the Rules-OCDS link.** This is the substantive contribution — most OCDS implementations don't make this crosswalk explicit. OCP will care.
- **Six review questions** (up from five). The new question is OCDS version target (1.1.5 vs 1.2-dev) which is now relevant because v0.2 references 1.2-dev codelists in the Vocab Translations sheet.
- **The OCID prefix question is now explicit** — based on observing that NSW has `43qwtd` registered. Earlier draft phrased it vaguely.
- **Working pipeline is mentioned** — gives concrete proof of feasibility, not just spec work.
- **NSW failure mode is acknowledged respectfully** — frames it as a learning rather than a critique.
- **Civil society framing is sharper** — explicitly references IRM's "systematically included" language. Strengthens the legitimacy of the engagement.
- **Reasonable expectations on response time** — OCP Helpdesk typically responds in 1–3 weeks. Don't follow up by re-sending; reply to the thread if needed after 3 weeks.
- Strip these notes before sending. Send from a real address with reply-to that you check.
