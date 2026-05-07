# OCP Helpdesk cover email — DRAFT

**To:** helpdesk@open-contracting.org
**From:** Manaaki Walker-Tepania, Project Unify
**Subject:** Request for review — draft NZ-OCDS mapping (GETS data, NZ Government Procurement Rules)

---

Kia ora,

I'm working on **Project Unify**, a New Zealand procurement intelligence platform built on Palantir Foundry. We're producing a working OCDS-compliant feed against publicly available GETS (Government Electronic Tenders Service) data, with the aim of helping deliver against NZ's OGP commitment **NZ0029** — *Improve Government Procurement Transparency* — ahead of its current 2030 implementation timeline.

NZ0029 explicitly commits to OCDS alignment but the IRM midterm review notes "specification of new mandatory fields for disclosure have yet to be determined". Civil society (Transparency International NZ) has been publicly critical that no significant progress has been made in four years. I'd like Project Unify's draft mapping to be reviewed by OCP before we ship it to MBIE/NZGP or publish it openly.

## What I'm sharing

Attached: **`ocds-nz-mapping-v0.1.xlsx`** — a draft NZ-OCDS field-level mapping with six sheets:

1. **README** — methodology and sources
2. **OCDS Mapping** — 91 OCDS 1.1.5 paths with status (Direct / Derived / Vocab Translation / Constant / NZ Extension / Template-sourced / Rule-mandated / Gap), each with a GETS source field reference and a corresponding NZ Government Procurement Rule reference where applicable
3. **Vocab Translations** — 22 codelist translations between GETS values and OCDS controlled lists
4. **NZ Extensions** — 14 proposed NZ extensions, each anchored to a specific NZ Rule rather than vendor preference
5. **Rules Inventory** — all 47 NZ Procurement Rules cross-referenced for OCDS relevance
6. **Templates Inventory** — 31 NZGP Approved Government Model Templates inventoried for OCDS field coverage

## The framing

The core insight that drove this work: **the NZ Government Procurement Rules already mandate the data OCDS expects.** Out of the 91 mapped paths:

- 23 Direct + 13 Derived = data flows from GETS today
- 19 Rule-mandated = the data is required to exist by law but isn't structurally published
- 14 Template-sourced = captured in mandatory NZGP templates but not centrally published
- 14 NZ Extension proposals (each Rule-anchored)
- Small remainder of Constants / Vocab Translations / Gaps

So OCDS-NZ alignment isn't a new data-collection burden — it's a structured-publication layer over data the Rules already demand. We think this materially changes the political conversation in NZ.

## Specific things I'd value your review on

1. **Procurement method mapping**: I've drafted RFT → `open`, RFP → `selective`, RFQ → `limited`. Is this defensible, or is there a clearer convention in implementations you've reviewed?
2. **Release tag strategy**: GETS award notices carry both tender and award data; I've proposed emitting releases with `["award"]` (or `["awardCancellation"]` for Not Awarded). Is this consistent with the OCP guidance?
3. **NZ extensions**: 14 proposed extensions in the spreadsheet. I'd particularly value feedback on `nz-tender-coverage` (AoG/Cluster/Syndicated/Sole), `nz-economic-benefits` (Rule 8 mandates ≥10% evaluation weighting), and `nz-mandate-level` (which tier of Rules compliance applies to the agency).
4. **Honest gaps**: I've flagged planning, contract performance, and bids sections as largely unrecoverable from current GETS data. Is this the right way to declare those gaps in a published feed?
5. **OCID strategy**: I've proposed `ocds-nz-gets-{rfxId}` as the deterministic OCID. Is this the right shape and is the prefix `ocds-nz-gets-` available, or should it be coordinated with NZGP first?

## Context that might help

- Foundry's Pipeline Builder gives us visual data-lineage by construction, so every OCDS field has a clickable trail back to source — that's the probity story we want to lead with when we approach MBIE/NZGP.
- We're a small team (currently solo) operating outside government, so this is genuinely civil-society-facing implementation work.
- We haven't approached MBIE yet. We want OCP review and (separately) Transparency NZ briefing first, so that any government conversation starts from a position of independent technical validation.

A 30-minute video call would be great if your schedule permits, but written feedback on the spreadsheet would also be enormously helpful.

Ngā mihi,

Manaaki Walker-Tepania
Project Unify
[contact details]

---

## Attachments
- `ocds-nz-mapping-v0.1.xlsx`
- (optional) Project Unify one-pager once drafted

## Notes for the sender (not part of the email)

- Keep the subject line and opening factual. OCP Helpdesk receives many requests; the NZ0029 + Rules-anchored framing differentiates this immediately.
- Don't oversell the demo. The mapping itself is the substance; the working pipeline is later.
- Tone: collegial peer asking for review, not vendor pitching. OCP's role is technical validation — they're not the audience for the moat narrative.
- Send from a personal/professional address that's easy to reply to. If sending from a Project Unify address, include reply-to with your direct email.
- If they take 2+ weeks to respond (typical), don't follow up by re-sending — instead reply to the same thread with "any questions while you review?"
