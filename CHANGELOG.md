# Changelog

All notable changes to the NZ-OCDS Mapping are documented in this file.
Versions follow [Semantic Versioning](https://semver.org/) for public releases (v1.0.0+);
pre-1.0 versions track research milestones.

## [v0.4] — 2026-05-07

### Added

- **OCDS Mapping sheet expanded** from 91 to 114 paths. Each of the 18 proposed NZ extensions now appears as individual rows under the relevant OCDS section (parties, tender, awards, contracts).
  - Parties: 5 new extension rows (Te Reo names, agency tier, mandate level, eInvoicing capability, NZBN resolver)
  - Tender: 12 new extension rows (Te Reo title, coverage, procurement-method-detail, contracting-model, secondary-procurement, opt-out rationale, exemption rationale, Treaty exception, prequalification, economic benefits, broader outcomes, GETS source)
  - Awards: 3 new extension rows (economic benefits at award, secondary procurement flag, Treaty exception flag)
  - Contracts: 3 new extension rows (contracting model, CMS fields per Rule 34, prompt-payment per Rule 36)
- Status mix now shows 31 NZ Extension rows (up from 8 in v0.3).

### Notes

- The `.xlsx` is a generated artefact. Source of truth is `mapping/build_ocds_mapping.py`.

## [v0.3] — 2026-05-07

### Added

- **4 new NZ extensions** sourced from glossary mining of the NZ Government Procurement Rules:
  - `nz-treaty-of-waitangi-exception` — formal Te Tiriti exception in NZ international trade agreements; distinct from Rule 11 opt-out and Rule 12 exemption
  - `nz-procurement-method-detail` — sub-typing for OCDS procurementMethod codes (competitive-dialogue, lean-agile-procurement with Big Room Event, multi-step-roi-rfp etc.)
  - `nz-contracting-model` — orthogonal to procurement method (outcomes-based-relational, lean-agile, commissioning, social-investment-outcomes, collaborative-contract)
  - `nz-secondary-procurement` — formal NZ term for panel call-offs (Rules 22, 12)
- 9 new vocab translation rows including provider→supplier (social services), tender watch codes = UNSPSC, ROI = Expression of Interest, relational = outcomes-based contract, plus refined procurement method mapping with practitioner-corrected logic (Competition_Type primary signal; RFx_Type → procurementMethodDetails).
- Lifecycle citation from glossary's `sourcing` definition (planning → market research → approaching market → evaluating → negotiating → contracting).

### Refined

- `nz-agency-tier` aligned to the four formal taxonomies in the Rules glossary: public-service / public-sector / state-sector / state-services.
- `nz-economic-benefits` — Trans-Tasman scope flag; per glossary, "New Zealand business" for Rule 8 purposes formally includes Australian business.
- Procurement method mapping now reflects practitioner feedback: GETS Competition_Type is the primary signal; RFx_Type carried in procurementMethodDetails as free text. Multi-stage processes (ROI → RFP/RFT) modelled as one OCID with stage-tagged releases over time.

### Sources added

- NZ Government Procurement Rules 5th edition Glossary (pages 83–103)
- Rule 10's enumeration of compliant procurement approaches (page 28)
- Rules 27–36 (Approaching the market section)

## [v0.2] — 2026-05-07

### Added

- **Codelist references in Vocab Translations**: each entry now links to the authoritative codelist file in `open-contracting/standard 1.2-dev` on GitHub (e.g. `method.csv`, `tenderStatus.csv`). Expanded from 22 to 38 entries.
- **Publishing Governance sheet (new)** — 8-step publishing process and 8 roles, NZ-localised from NSW Open Data Publishing Guidelines V3.0 (Nov 2022).
- **Sensitivity Classification sheet (new)** — 14-row field-level publish/redact/aggregate/suppress policy anchored to NZGP Rule 5, OIA 1982 s9, Privacy Act 2020, NSW IC Guidelines V2.3.

### Strategic context

- NSW Treasury OCDS publication on the OCP Data Registry studied. 20 years of data (2005–2025), 29,391 tenders, but status: "no longer updated by the publisher" with documented quality issues. Reference and cautionary tale.

## [v0.1] — 2026-05-06

### Added

- Initial draft mapping: 91 OCDS paths × {GETS source, Rule reference, status, notes}
- 22 vocabulary translations
- 14 NZ extension proposals
- All 47 NZ Procurement Rules cross-referenced
- 31 NZGP Approved Government Model Templates inventoried

### Methodology

Built from:
- OCDS 1.1.5 release schema (1,321 fields)
- MBIE GETS schema (32 fields across 4 tables)
- NZ Government Procurement Rules 5th edition (47 rules + appendices)
- NZGP Approved Government Model Templates inventory
- OGP commitment NZ0029 IRM midterm review

### The core finding

The NZ Procurement Rules already mandate the data OCDS expects. ~80% of OCDS coverage closes by structuring data the Rules already require to exist.

---

## Version naming convention

- **v0.x** — Pre-public-feed research milestones. Each version represents a substantive structural addition (new extensions, new sheets, refined methodology).
- **v1.0** — First version submitted to OCP Helpdesk for formal review.
- **v1.x** — Iterations incorporating OCP feedback.
- **v2.0** — First public release (post-feed launch). Major versions thereafter follow semver.
