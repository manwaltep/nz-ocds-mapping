"""
Build the NZ-OCDS Mapping spreadsheet from:
- The OCDS 1.1.5 release schema CSV + 1.2-dev codelists (open-contracting/standard on GitHub)
- The MBIE GETS schema (manually transcribed)
- The NZ Government Procurement Rules 5th edition (mandatory data references)
- The NZGP Approved Government Model Templates inventory
- The NSW Government Open Data Publishing Guidelines V3.0 (process governance)
- The NSW Government Information Classification Labelling and Handling Guidelines (sensitivity)

Output: /Users/manaakiwalker-tepania/Documents/Work/claude-code/palantir-aip/data-tmp/ocds-nz-mapping-v0.3.xlsx

Eight sheets:
  1. README                    — summary, methodology, sources
  2. OCDS Mapping              — field-by-field crosswalk
  3. Vocab Translations        — codelist translations with authoritative OCDS codelist references
  4. NZ Extensions             — proposed extensions with Rule anchors
  5. Rules Inventory           — all 47 Rules with OCDS-relevance commentary
  6. Templates Inventory       — NZGP A-GMTs with OCDS-relevance commentary
  7. Publishing Governance     — NZ-localised 8-step process (NSW Open Data Guidelines adapted)
  8. Sensitivity Classification— what to publish / redact / suppress (Rule 5 + OIA + NSW IC)
"""

import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


SCHEMA_CSV = "/Users/manaakiwalker-tepania/Downloads/release-schema.csv"
OUTPUT = "/Users/manaakiwalker-tepania/Documents/Work/claude-code/palantir-aip/data-tmp/ocds-nz-mapping-v0.4.xlsx"
CODELIST_BASE = "https://github.com/open-contracting/standard/blob/1.2-dev/schema/codelists"


# ── Style helpers ────────────────────────────────────────────────────────────

THIN = Side(border_style="thin", color="C0C0C0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADER_FILL = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
SECTION_FILL = PatternFill(start_color="E5E7EB", end_color="E5E7EB", fill_type="solid")
SECTION_FONT = Font(bold=True, size=11)

STATUS_COLOURS = {
    "Direct":            "10B981",  # green   — value flows straight from GETS
    "Derived":           "06B6D4",  # cyan    — computed from GETS fields
    "Vocab Translation": "8B5CF6",  # purple  — controlled list translation
    "Constant":          "6B7280",  # grey    — hardcoded (e.g. NZD)
    "NZ Extension":      "F59E0B",  # amber   — extension proposal needed
    "Template-sourced":  "3B82F6",  # blue    — captured in NZGP A-GMTs but not GETS
    "Rule-mandated":     "EC4899",  # pink    — mandated by Rules but no current source
    "Gap":               "EF4444",  # red     — not collected anywhere
}


def apply_header(ws: Worksheet, row: int, headers: list[str], widths: list[int]) -> None:
    for i, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = ws.cell(row=row + 1, column=2)


def write_row(ws: Worksheet, row: int, values: list, status: str | None = None) -> None:
    for i, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=i, value=v)
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        c.border = BORDER
        c.font = Font(size=10)
    if status and status in STATUS_COLOURS:
        # Highlight the status column (assume it's column 7 — adjust per sheet if needed)
        pass


# ── Sheet 1: README ──────────────────────────────────────────────────────────

def build_readme(ws: Worksheet) -> None:
    ws.title = "README"
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 110

    rows = [
        ("NZ-OCDS Mapping", "v0.4 — DRAFT FOR REVIEW"),
        ("Maintained by", "Project Unify"),
        ("Status", "Draft proposal. Not yet endorsed by NZGP / MBIE / OCP. Open for comment."),
        ("", ""),
        ("PURPOSE", ""),
        ("", "A field-level crosswalk between the NZ Government Electronic Tenders Service (GETS) "
              "schema, the NZ Government Procurement Rules (5th edition, 2025), the NZGP Approved "
              "Government Model Templates (A-GMTs), and the Open Contracting Data Standard (OCDS) "
              "release schema 1.1.5."),
        ("", ""),
        ("WHY THIS EXISTS", ""),
        ("", "NZ committed to OCDS alignment under OGP commitment NZ0029. As of 2026 the field "
              "specification remains 'yet to be determined' (per IRM midterm review) and full "
              "implementation is targeted for 2030. This document is a working draft that "
              "demonstrates a complete mapping is achievable today using only public artefacts."),
        ("", "Critically — the Rules already MANDATE the data OCDS expects. OCDS compliance is "
              "therefore not a new burden on agencies; it is a structured way of publishing data "
              "that the Rules already require to exist."),
        ("", ""),
        ("METHODOLOGY", ""),
        ("", "1. Take every OCDS 1.1.5 release-schema field (1,321 paths across 9 sections)."),
        ("", "2. For each, identify whether: (a) GETS provides the data today, (b) a Rule "
              "mandates the data exists, (c) an A-GMT captures the data, or (d) it's a genuine gap."),
        ("", "3. Where GETS values need translation to OCDS codelists, document the mapping "
              "in the Vocab Translations sheet."),
        ("", "4. Where the data is mandated but doesn't fit native OCDS, propose an NZ extension "
              "anchored to a specific Rule (NZ Extensions sheet)."),
        ("", ""),
        ("STATUS LEGEND (column G of OCDS Mapping sheet)", ""),
        ("Direct", "Value flows straight from a GETS field"),
        ("Derived", "Computed from one or more GETS fields"),
        ("Vocab Translation", "GETS value translated via a controlled-list mapping"),
        ("Constant", "Hardcoded (e.g. currency = NZD)"),
        ("NZ Extension", "Proposed NZ-specific extension; data exists per Rules but no native OCDS field"),
        ("Template-sourced", "Captured in NZGP A-GMT (Procurement Plan / RFx / GMC / CMP) but not currently published structurally"),
        ("Rule-mandated", "Mandated by a specific Rule but no current structured source"),
        ("Gap", "Not collected by GETS, Rules, or templates"),
        ("", ""),
        ("SOURCES", ""),
        ("OCDS schema", "https://standard.open-contracting.org/1.1/en/schema/release/ (release-schema.json, also via release-schema.csv)"),
        ("GETS open data", "https://www.mbie.govt.nz/cross-government-functions/new-zealand-government-procurement-and-property/open-data"),
        ("GETS schema", "MBIE 'GETS schema and documentation' (Field Information sheet, .xlsx)"),
        ("Rules", "Government Procurement Rules — 5th edition, August 2025 (ISBN 978-1-991143-00-6)"),
        ("Templates inventory", "https://www.procurement.govt.nz/templates/"),
        ("OGP commitment", "https://www.opengovpartnership.org/members/new-zealand/commitments/NZ0029/"),
        ("Civil society context", "Transparency NZ — 'Four years of Open Procurement Data'"),
        ("OCDS codelists (1.2-dev)", "https://github.com/open-contracting/standard/tree/1.2-dev/schema/codelists"),
        ("NSW publication (reference + cautionary tale)", "https://data.open-contracting.org/en/publication/11"),
        ("NSW Open Data Publishing Guidelines V3.0", "data.nsw.gov.au — adapted for Publishing Governance sheet"),
        ("NSW Information Classification Labelling and Handling Guidelines V2.3 (2021)", "Adapted for Sensitivity Classification sheet"),
        ("", ""),
        ("v0.2 ADDITIONS (relative to v0.1)", ""),
        ("Vocab Translations", "Added 'Codelist File' + 'Codelist Source URL' columns linking each translation to authoritative OCDS codelist on GitHub. Expanded from 22 to 38 entries. Targeted OCDS 1.2-dev codelists."),
        ("Publishing Governance (new sheet)", "8-step publishing process + 8 roles, adapted from NSW Open Data Publishing Guidelines V3.0 with NZ localisation (OIA in place of GIPA, NZGP/MBIE roles, OCDS-specific concerns)."),
        ("Sensitivity Classification (new sheet)", "14-row field-level classification (Publish/Redact/Aggregate/Suppress) anchored against NZGP Rule 5, OIA s9, Privacy Act 2020, NSW IC Guidelines. Plus 7-step decision process."),
        ("Strategic context update", "NSW eTendering has been publishing OCDS data for 20 years (2005-2025) but is 'no longer updated by the publisher' and has documented quality issues. Reference + cautionary tale: proves feasibility, reveals failure modes that NZ should design against."),
        ("", ""),
        ("v0.3 ADDITIONS (relative to v0.2)", ""),
        ("New extension: nz-treaty-of-waitangi-exception", "NZ is party to international agreements with formal Te Tiriti o Waitangi exceptions for Māori-favourable measures. Distinct from Rule 11 opt-out and Rule 12 exemption. Anchored to Government Procurement Charter + Rule 1 (Principles) + Glossary 'Te Tiriti o Waitangi/Treaty of Waitangi Exception' definition."),
        ("New extension: nz-procurement-method-detail", "Sub-typing for the OCDS procurementMethod codelist values (open/selective/limited/direct), with explicit values for Competitive Dialogue (suppliers paid for participation), Lean Agile Procurement (Big Room Event), and multi-step processes (ROI → RFP/RFT). Glossary-anchored: Rule 10 + glossary definitions."),
        ("New extension: nz-contracting-model", "Orthogonal to procurement method — captures the contract structure regardless of selection process. Values: outcomes-based-relational, lean-agile, commissioning, social-investment. Anchored to Rule 10's enumeration of compliant approaches and the glossary's 'relational contract' definition (= outcomes-based)."),
        ("New extension: nz-secondary-procurement", "Formal NZ term for panel call-offs (purchases from Panel/AoG/CC/Syndicated). Rule 22 + Rule 12 + Glossary anchor."),
        ("Refined nz-agency-tier", "Aligned to the four formal taxonomies in the Rules glossary: public-service / public-sector / state-sector / state-services."),
        ("Refined nz-economic-benefits", "Trans-Tasman scope clarified — 'New Zealand business' for Rule 8 purposes formally includes Australian business per the glossary."),
        ("Procurement method mapping refined", "Practitioner-corrected mapping: Competition_Type is the primary signal for OCDS procurementMethod; RFx_Type carried in procurementMethodDetails (free text). Multi-stage processes (ROI → RFP/RFT) modelled as one OCID with stage-tagged releases over time. Closed competition pre-qualified → selective; closed competition with Rule 12 exemption → limited or direct."),
        ("New vocab translations (4)", "provider → supplier (social services); relational contract = outcomes-based contract; ROI = Expression of Interest = first formal stage of multistep; tender watch codes = UNSPSC."),
        ("Lifecycle citation", "Glossary definition of 'sourcing' (planning → market research → approaching market → evaluating → negotiating → contracting) anchors the OCDS release-tag lifecycle modelling."),
        ("Sources added", "NZ Government Procurement Rules 5th edition Glossary (pages 83–103). Rule 10's enumeration of compliant procurement approaches (page 28). Rules 27–36 (Approaching the market section)."),
        ("", ""),
        ("v0.4 ADDITIONS (relative to v0.3)", ""),
        ("OCDS Mapping sheet expanded", "Each of the 18 NZ extensions now appears as individual rows in the OCDS Mapping sheet under the relevant OCDS section (parties, tender, awards, contracts). Previously, extensions were only listed in the NZ Extensions sheet. This makes the OCDS Mapping sheet a complete picture: for any OCDS object, you can see both the core fields AND the proposed NZ extension fields in one place."),
        ("Extension field rows added", "20+ new rows distributed across parties (5), tender (12), awards (3), and contracts (3). All marked with status 'NZ Extension' and reference the parent extension ID in the NZ Extensions sheet."),
        ("Field-level paths exposed", "Each extension now has explicit OCDS-style paths (e.g. tender.coverage, parties[].agencyTier, contracts[].promptPayment). These would be the actual JSON paths in published OCDS releases."),
        ("", ""),
        ("NEXT STEPS", ""),
        ("", "1. Send this draft to OCP Helpdesk (helpdesk@open-contracting.org) for review."),
        ("", "2. Brief Transparency NZ — they have been publicly seeking exactly this analysis."),
        ("", "3. Pilot a working Pipeline Builder transform that produces OCDS releases from GETS data."),
        ("", "4. Approach NZGP/MBIE with the working pilot + this mapping + OCP-reviewed status."),
    ]
    for i, (k, v) in enumerate(rows, start=1):
        a = ws.cell(row=i, column=1, value=k)
        b = ws.cell(row=i, column=2, value=v)
        a.font = Font(bold=True, size=11)
        a.alignment = Alignment(vertical="top", wrap_text=True)
        b.alignment = Alignment(vertical="top", wrap_text=True)
        b.font = Font(size=10)
        if k in ("PURPOSE", "WHY THIS EXISTS", "METHODOLOGY", "STATUS LEGEND (column G of OCDS Mapping sheet)", "SOURCES", "NEXT STEPS"):
            a.fill = SECTION_FILL


# ── Sheet 2: OCDS Mapping ────────────────────────────────────────────────────
# Column layout:
#   A: OCDS Section
#   B: OCDS Path
#   C: OCDS Type
#   D: OCDS Description (from spec, abbreviated)
#   E: GETS Source Field
#   F: Rule Reference
#   G: Status
#   H: Mapping / Derivation Notes
#   I: NZ Extension ID (if applicable)

# The mapping itself. Each entry: (section, path, type, gets_source, rule, status, notes, ext)
# Rather than enumerate all 1,321, focus on the meaningful ~200 fields procurement publishers care about.

MAPPINGS = [
    # ── Top-level release metadata
    ("(top)", "ocid", "string", None, None, "Derived",
     "ocds-nz-gets-{rfxId}. Deterministic prefix per OCP guidance + GETS rfxId as the unique procurement identifier.", None),
    ("(top)", "id", "string", None, None, "Derived",
     "{ocid}-{releaseDate}-{tag} — unique within ocid scope.", None),
    ("(top)", "date", "date-time", "Report Date", None, "Direct",
     "Parse YYYYMMDD → ISO 8601. GETS only carries date precision (no time).", None),
    ("(top)", "tag", "array", None, None, "Derived",
     "Determined by GETS event type: tender notice → ['tender']; award notice (Awarded) → ['award']; "
     "award notice (Not Awarded) → ['awardCancellation']; FPO publication → ['planning'].", None),
    ("(top)", "initiationType", "string", None, None, "Constant",
     "Always 'tender' for GETS-sourced data.", None),
    ("(top)", "language", "string", None, None, "Constant",
     "'en' (with Te Reo strings carried in extension fields — see nz-te-reo-names).", None),

    # ── parties (organisations involved)
    ("parties", "parties[].id", "string", None, None, "Derived",
     "Slug of organisation name + scheme. Stable per-party.", None),
    ("parties", "parties[].name", "string", "Posting Agency / Business Name", "Rule 17(2)(a), Rule 32(2)(a-b)",
     "Direct", "Buyer = Posting Agency. Supplier = Business Name. Carry macron repair.", None),
    ("parties", "parties[].roles", "array", None, None, "Derived",
     "['buyer','procuringEntity'] for posting agency; ['supplier','tenderer'] for awarded supplier.", None),
    ("parties", "parties[].identifier.scheme", "string", None, "Rule 32(2)(i), Rule 34(2)(b)",
     "Constant", "'NZ-NZBN' for suppliers with NZBN. Crown agencies need a separate NZ-AGENCY scheme.", None),
    ("parties", "parties[].identifier.id", "string", "Supplier NZBN", "Rule 32(2)(i)",
     "Direct", "GETS Supplier NZBN. Per MBIE schema: not validated, may be Australian or international.", None),
    ("parties", "parties[].identifier.legalName", "string", None, None, "NZ Extension",
     "Legal name distinct from trading name. Available via NZBN registry.", "nz-nzbn-resolver"),
    ("parties", "parties[].address.streetAddress", "string", "Full Address", None, "Direct",
     "GETS supplier full address. Unstructured, may not adhere to formatting standards.", None),
    ("parties", "parties[].address.countryName", "string", "Country", None, "Direct",
     "GETS Country. Caveat (per MBIE schema): 'does not designate company nationality or ownership'.", None),
    ("parties", "parties[].contactPoint.url", "string", "Website", None, "Direct",
     "GETS Website (suppliers only).", None),
    ("parties", "parties[].details (NZ ext)", "object", "Department", "Rule 17(2)(b)",
     "NZ Extension", "Department within posting agency, contact person details.", "nz-agency-details"),
    # ── v0.4: extension fields on parties[] ───────────────────────────────────
    ("parties", "parties[].nameTeReoMaori (ext)", "string", "Posting Agency / Business Name", "Rule 1; Glossary 'Te Tiriti o Waitangi Exception'",
     "NZ Extension", "Bilingual party name in Te Reo Māori. Fixes macron rendering broken at GETS source.", "nz-te-reo-names"),
    ("parties", "parties[].agencyTier (ext)", "string", "GETS Agency List Report tier", "Application of Rules — Part Four; Glossary 'public sector', 'public service', 'state sector', 'state services'",
     "NZ Extension", "NZ public-sector taxonomy (4-tier glossary alignment): public-service / public-sector / state-sector / state-services + sub-categories.", "nz-agency-tier"),
    ("parties", "parties[].mandateLevel (ext)", "string", "(derived from agency tier)", "Application of Rules — Part Four sections A and B",
     "NZ Extension", "Compliance tier: mandated / expected / encouraged.", "nz-mandate-level"),
    ("parties", "parties[].einvoicingCapability (ext)", "object", "(derived; future: Peppol registry)", "Rule 44 — eInvoicing capability",
     "NZ Extension", "Peppol capability flag + ID + capability date. Mandatory for 2,000+ invoice agencies from 1 Jan 2026.", "nz-einvoicing-capability"),
    ("parties", "parties[].nzbnResolved (ext)", "object", "Supplier_NZBN cross-referenced with NZBN registry", "Rule 17, Rule 32(2)(i), Rule 34(2)(b)",
     "NZ Extension", "NZBN-validated party resolution: legal name, entity type, registered status. MBIE's GETS schema notes raw NZBN field is not validated.", "nz-nzbn-resolver"),

    # ── buyer (synonym for the procuringEntity party — kept for backwards compat)
    ("buyer", "buyer.name", "string", "Posting Agency", "Rule 17(2)(a), Rule 32(2)(a)", "Direct",
     "Same as parties[].name where role=buyer.", None),
    ("buyer", "buyer.id", "string", None, None, "Derived",
     "Reference to parties[].id where role=buyer.", None),

    # ── planning (179 fields in spec; almost zero in GETS, but Rules mandate the data exists)
    ("planning", "planning.rationale", "string", None, "Rule 6(3)(a) — procurement objective",
     "Template-sourced", "Captured in 'Procurement plan template' (NZGP A-GMT) but not published.", None),
    ("planning", "planning.budget.amount.amount", "number", None, "Rule 7 — estimating monetary value",
     "Template-sourced", "Mandated to be in business case OR procurement plan. Not published in GETS for tender stage.", None),
    ("planning", "planning.budget.amount.currency", "string", None, None, "Constant", "'NZD'.", None),
    ("planning", "planning.budget.description", "string", None, "Rule 7 — value estimation rationale",
     "Template-sourced", "Captured in procurement plan template.", None),
    ("planning", "planning.budget.project", "string", None, None, "Template-sourced",
     "Project name from procurement plan / business case.", None),
    ("planning", "planning.budget.projectID", "string", None, None, "Template-sourced",
     "Reference Number field carries this for some procurements.", None),
    ("planning", "planning.documents[]", "array", None, "Rule 17(2)(d), Rule 47 — A-GMT use is mandatory",
     "Template-sourced", "Procurement plan, business case, market analysis. Mandated; not centrally published.", None),
    ("planning", "planning.milestones[]", "array", None, "Rule 17 'good practice' timeframe details",
     "Rule-mandated", "Indicative timeframes (deadline for queries, presentations, debrief, contract start) — Rule 17 'should' include these in NoP.", None),
    ("planning", "planning.rationale (extension)", "string", None, "Rule 6(3)(b) — market analysis",
     "NZ Extension", "Market analysis findings. Required by Rule 6.", "nz-market-analysis"),
    ("planning", "planning.rationale (extension)", "string", None, "Rule 6(3)(c) — demand analysis",
     "NZ Extension", "Demand analysis. Required by Rule 6.", "nz-demand-analysis"),
    ("planning", "planning.rationale (extension)", "string", None, "Rule 6(3)(d) — sourcing approach",
     "NZ Extension", "Sourcing approach decision. Required by Rule 6.", "nz-sourcing-approach"),
    ("planning", "planning.rationale (extension)", "string", None, "Rule 6(3)(e), Rule 8 — economic benefits",
     "NZ Extension", "Economic benefits sought (≥10% evaluation weighting). Required by Rules 6 and 8.", "nz-economic-benefits"),
    ("planning", "planning.rationale (extension)", "string", None, "Rule 6(3)(f), Rule 26 — risk identification",
     "NZ Extension", "Risk identification including national security risks.", "nz-risk-assessment"),

    # ── tender (the most-populated section from GETS)
    ("tender", "tender.id", "string", "RFx ID", None, "Direct", "GETS RFx ID.", None),
    ("tender", "tender.title", "string", "Title", "Rule 17(2)(c)", "Direct", "GETS Title (with macron repair).", None),
    ("tender", "tender.description", "string", "Overview", "Rule 17(2)(d)", "Direct",
     "GETS Overview. Rule 17 also requires technical specifications and outcomes description.", None),
    ("tender", "tender.status", "string", None, None, "Derived",
     "From dates + Award Type: Open Date passed + Close Date future → 'active'; "
     "Close Date passed + Award Type Awarded → 'complete'; Award Type Not Awarded → 'unsuccessful'.", None),
    ("tender", "tender.procurementMethod", "string", "RFx Type + Competition Type", None, "Vocab Translation",
     "RFT + Open → 'open'; RFP + Open → 'selective'; RFQ → 'limited'; Closed Competition → 'limited'. "
     "See Vocab Translations sheet.", None),
    ("tender", "tender.procurementMethodDetails", "string", "RFx Type", None, "Direct",
     "Preserve original GETS term (Request for Tenders / Proposals / Quotations / Award Notice).", None),
    ("tender", "tender.procurementMethodRationale", "string", "Tender Coverage", None, "NZ Extension",
     "AoG / Cluster / Syndicated / Sole / On-behalf — see nz-tender-coverage.", "nz-tender-coverage"),
    ("tender", "tender.mainProcurementCategory", "string", None, None, "Derived",
     "From UNSPSC family code: 'goods' / 'services' / 'works'.", None),
    ("tender", "tender.value.amount", "number", None, "Rule 7 — estimated value",
     "Rule-mandated", "Estimated total monetary value. Lives in business case / procurement plan; should be published with NoP per Rule 17(2)(g).", None),
    ("tender", "tender.value.currency", "string", None, None, "Constant", "'NZD'.", None),
    ("tender", "tender.tenderPeriod.startDate", "string", "Open Date", "Rule 17(2)(l)", "Direct",
     "Parse YYYYMMDD → ISO 8601.", None),
    ("tender", "tender.tenderPeriod.endDate", "string", "Close Date", "Rule 17(2)(l), Rule 16 — sufficient time",
     "Direct", "Parse YYYYMMDD → ISO 8601.", None),
    ("tender", "tender.enquiryPeriod.endDate", "string", None, "Rule 17 'should' — query deadline",
     "Template-sourced", "Captured in RFx templates.", None),
    ("tender", "tender.eligibilityCriteria", "string", "Prequalification Required?", "Rule 14, Rule 17(2)(i), Rule 23",
     "Derived", "If 'Yes' → 'Prequalification required (Rule 23)'. Pre-conditions per Rule 14 may also apply.", None),
    ("tender", "tender.awardCriteria", "string", None, "Rule 17(2)(k) — evaluation criteria",
     "Rule-mandated", "Evaluation criteria + relative weightings. Mandated in NoP by Rule 17. Not in GETS.", None),
    ("tender", "tender.awardCriteriaDetails", "string", None, "Rule 17(2)(k)",
     "Rule-mandated", "Detailed evaluation methodology.", None),
    ("tender", "tender.submissionMethod", "array", "Alternative Physical Tender Box Delivery Address", "Rule 17(2)(m)",
     "Derived", "If 'GETS website' → ['electronicSubmission']; physical address → ['written'].", None),
    ("tender", "tender.submissionMethodDetails", "string", "Alternative Physical Tender Box Delivery Address",
     "Rule 17(2)(l-m)", "Direct", "Submission instructions.", None),
    ("tender", "tender.documents[]", "array", None, "Rule 17(2)(d), Rule 47", "Template-sourced",
     "Procurement notice, RFx template, T&Cs, Schedule 2 etc. Available via NZGP A-GMTs.", None),
    ("tender", "tender.items[].id", "integer", None, None, "Derived",
     "Sequential within a tender, linking to UNSPSC entries.", None),
    ("tender", "tender.items[].classification.scheme", "string", None, None, "Constant", "'UNSPSC'.", None),
    ("tender", "tender.items[].classification.id", "string", "UNSPSC Classification", None, "Direct",
     "UNSPSC Family Title/Class Code (8 digits).", None),
    ("tender", "tender.items[].classification.description", "string", "UNSPSC Description", None, "Direct",
     "UNSPSC Family Title/Class Title.", None),
    ("tender", "tender.items[].deliveryAddresses[].region", "string", "Region", None, "Direct",
     "GETS Region (NZ regions + 'New Zealand' + 'International').", None),
    ("tender", "tender.items[].deliveryAddresses[].countryName", "string", None, None, "Constant",
     "'New Zealand' unless Region = 'International'.", None),
    ("tender", "tender.numberOfTenderers", "integer", None, "Rule 30 — informing suppliers", "Rule-mandated",
     "Could be derived from supplier debrief data; not in GETS today.", None),
    ("tender", "tender.hasEnquiries", "boolean", None, "Rule 19 — responding to queries", "Rule-mandated",
     "Whether queries were received during the tender period.", None),
    ("tender", "tender.contractPeriod.startDate", "string", None, "Rule 17(2)(f) — contract length",
     "Template-sourced", "Anticipated contract start date — Rule 17 'should' include in NoP.", None),
    ("tender", "tender.contractPeriod.durationInDays", "integer", None, "Rule 17(2)(f)",
     "Template-sourced", "Estimated contract length / options (e.g. 3+2+1 years).", None),
    # ── v0.4: extension fields on tender ─────────────────────────────────────
    ("tender", "tender.titleTeReoMaori (ext)", "string", "(human-curated or auto-generated)", "Rule 1; Glossary",
     "NZ Extension", "Bilingual tender title in Te Reo Māori.", "nz-te-reo-names"),
    ("tender", "tender.coverage (ext)", "string", "GETS Tender_Coverage", "Rules 38, 39, 40, 22; Glossary 'AoG', 'Common Capability', 'Open/Closed Syndicated Contract'",
     "NZ Extension", "Procurement collaboration mechanism: all-of-government / common-capability / syndicated / sole-agency / on-behalf.", "nz-tender-coverage"),
    ("tender", "tender.procurementMethodDetail (ext)", "string", "GETS RFx_Type + Competition_Type + multi-stage flag", "Rule 10 enumeration; Glossary 'multi-step process', 'competitive dialogue', 'lean agile procurement'",
     "NZ Extension", "Sub-typing OCDS procurementMethod codes: single-stage-rft / single-stage-rfp / single-stage-rfq / multi-step-roi-rfp / multi-step-roi-rft / competitive-dialogue / lean-agile-procurement / panel-secondary-procurement / direct-from-panel / rule-12-exempt.", "nz-procurement-method-detail"),
    ("tender", "tender.contractingModel (ext)", "string", "(derived from tender description / contract template)", "Rule 10 enumeration; Glossary 'relational contract', 'social sector commissioning', 'social investment outcomes contract'",
     "NZ Extension", "Contract structure (orthogonal to selection process): standard / outcomes-based-relational / lean-agile / commissioning / social-investment-outcomes / collaborative-contract.", "nz-contracting-model"),
    ("tender", "tender.secondaryProcurement (ext)", "object", "(derived from Tender_Coverage + parent panel reference)", "Rules 12, 22; Glossary 'secondary procurement'",
     "NZ Extension", "Flag panel call-offs + parent arrangement type + parent RFx_ID. Reinforces relatedProcesses[].relationship='framework' modelling.", "nz-secondary-procurement"),
    ("tender", "tender.optOutRationale (ext)", "object", "(documented per Rule 11 rationale doc)", "Rule 11; Appendix 1",
     "NZ Extension", "Codelist of 13 valid Rule 11 opt-out reasons (between-agency / overseas / non-contractual / land-buildings / conditional-grant / international-development / public-services / central-financial-control / military-security etc.) + free-text justification.", "nz-opt-out-rationale"),
    ("tender", "tender.exemptionRationale (ext)", "object", "(documented per Rule 12 rationale doc)", "Rule 12; Appendix 2",
     "NZ Extension", "Codelist of 10 valid Rule 12 exemptions (emergency / post-open-process / only-one-supplier / judicial-order / additional-goods / prototype / commodity-market / exceptional / design-contest / market-led-proposal) + free-text justification.", "nz-exemption-rationale"),
    ("tender", "tender.treatyExceptionInvoked (ext)", "object", "(documented when invoked)", "Rule 1; Glossary 'Te Tiriti o Waitangi/Treaty of Waitangi Exception'; international trade agreements",
     "NZ Extension", "★ Distinct from Rule 11 opt-out and Rule 12 exemption. Formal Te Tiriti exception in NZ international trade agreements for Māori-favourable measures. Boolean flag + rationale + which agreement provides the exception.", "nz-treaty-of-waitangi-exception"),
    ("tender", "tender.prequalification (ext)", "object", "GETS Prequalification_Required + Pre-qualified Suppliers List reference", "Rules 14, 23",
     "NZ Extension", "Boolean flag + scheme name (e.g. SICP for ICT). Rule 23 governs Pre-qualified Suppliers List.", "nz-prequalification"),
    ("tender", "tender.economicBenefits (ext)", "object", "(captured in NoP per Rule 8)", "Rule 8; Glossary 'New Zealand business' (includes Australian for Rule 8)",
     "NZ Extension", "Mandatory ≥10% evaluation weighting. 7 benefit categories per Rule 8(4): workforce / SMEs / exports / industry-capability / innovation / sustainability / social-cultural-outcomes. Trans-Tasman scope flag.", "nz-economic-benefits"),
    ("tender", "tender.broaderOutcomes (ext)", "array", "(captured in NoP)", "Rule 8(4); Government Procurement Charter; Treaty/Te Tiriti commitments",
     "NZ Extension", "Cabinet-set procurement priorities: waste-reduction / living-wage / maori-business / pasifika-business / regional / apprenticeships / climate-emissions etc.", "nz-broader-outcomes"),
    ("tender", "tender.getsSource (ext)", "object", "GETS Link / RFx_ID", "Rules 17, 32, 37 (publish on GETS)",
     "NZ Extension", "Provenance back to original GETS notice: getsId + getsUrl. Probity/lineage trail.", "nz-gets-source"),

    # ── awards
    ("awards", "awards[].id", "string", None, None, "Derived",
     "{ocid}-award-{seq} or {rfxId}-{awardedDate}.", None),
    ("awards", "awards[].title", "string", "Title", None, "Direct", "Title of the awarded scope.", None),
    ("awards", "awards[].description", "string", "Comments", None, "Direct",
     "GETS Comments field. Caveat: awarded amount may also be embedded in this free-text field.", None),
    ("awards", "awards[].status", "string", "Award Type", None, "Vocab Translation",
     "'Awarded' → 'active'; 'Not Awarded' → 'unsuccessful'.", None),
    ("awards", "awards[].date", "string", "Awarded Date", "Rule 32(2)(d)", "Direct",
     "Parse YYYYMMDD → ISO 8601.", None),
    ("awards", "awards[].value.amount", "number", "Awarded Amount", "Rule 32(2)(f) — expected spend",
     "Direct", "GETS Awarded Amount. Note: Rule 32 mandates either expected spend OR highest/lowest offers — GETS captures only awarded amount.", None),
    ("awards", "awards[].value.currency", "string", None, None, "Constant", "'NZD'.", None),
    ("awards", "awards[].suppliers[]", "array", "Supplier table (joined on RFx ID)", "Rule 32(2)(b)",
     "Derived", "Array of party references where role=supplier.", None),
    ("awards", "awards[].items[]", "array", "UNSPSC + Region tables", None, "Direct",
     "Same items as on the tender (per-supplier allocation if known).", None),
    ("awards", "awards[].contractPeriod.startDate", "string", None, "Rule 32(2)(e) — term of contract",
     "Rule-mandated", "Contract start date. Rule 32 mandates 'term of contract' but GETS doesn't capture it.", None),
    ("awards", "awards[].contractPeriod.durationInDays", "integer", None, "Rule 32(2)(e)",
     "Rule-mandated", "Contract term. NEW field gap inside MBIE's own system.", None),
    ("awards", "awards[].relatedLots", "array", None, None, "Gap", "GETS doesn't model lots.", None),
    ("awards", "awards[].documents[]", "array", None, None, "Template-sourced",
     "Government Model Contract documents (GMC Form 1/2 Goods/Services).", None),
    # ── v0.4: extension fields on awards ──────────────────────────────────────
    ("awards", "awards[].economicBenefits (ext)", "object", "(captured in award rationale per Rule 8(5)(d))", "Rule 8(5)(d), Rule 32(2)(j)",
     "NZ Extension", "Economic benefits agreed at award + contract provisions to deliver them. Rule 32(2)(j) requires this in the award notice.", "nz-economic-benefits"),
    ("awards", "awards[].secondaryProcurement (ext)", "object", "(derived from award context)", "Rules 12, 22, 32(2)(g)",
     "NZ Extension", "Flag award as a panel call-off; reference parent arrangement.", "nz-secondary-procurement"),
    ("awards", "awards[].treatyExceptionInvoked (ext)", "object", "(documented when invoked)", "Rule 1; Glossary",
     "NZ Extension", "Treaty exception flag at award stage (matches tender.treatyExceptionInvoked).", "nz-treaty-of-waitangi-exception"),

    # ── contracts (500 fields, all from agency CMS — Rule 34/35 mandate this data exists)
    ("contracts", "contracts[].id", "string", None, "Rule 34", "Rule-mandated",
     "Contract identifier from agency Contract Management System.", None),
    ("contracts", "contracts[].awardID", "string", None, None, "Rule-mandated",
     "Reference to awards[].id.", None),
    ("contracts", "contracts[].title", "string", None, "Rule 34(2)(a) — supplier name on contract",
     "Rule-mandated", "Mandated in CMS by Rule 34.", None),
    ("contracts", "contracts[].status", "string", None, None, "Rule-mandated",
     "Codelist: pending / active / cancelled / terminated.", None),
    ("contracts", "contracts[].period.startDate", "string", None, "Rule 34(2)(g)",
     "Rule-mandated", "Start date — mandatory CMS field.", None),
    ("contracts", "contracts[].period.endDate", "string", None, "Rule 34(2)(g)",
     "Rule-mandated", "End date — mandatory CMS field.", None),
    ("contracts", "contracts[].value.amount", "number", None, "Rule 34(2)(h)",
     "Rule-mandated", "Actual amount spent — mandatory CMS field per Rule 34.", None),
    ("contracts", "contracts[].dateSigned", "string", None, None, "Rule-mandated",
     "Date all parties signed. Implicit reference: 'within 30 business days of all parties signing the contract' (Rule 32).", None),
    ("contracts", "contracts[].documents[]", "array", None, "Rule 47 — A-GMT use mandatory",
     "Template-sourced", "Government Model Contract (GMC). Specific A-GMT depends on Crown vs non-Crown, Goods vs Services.", None),
    ("contracts", "contracts[].milestones[]", "array", None, "Rule 35(2) — performance metrics",
     "Rule-mandated", "Performance milestones. Rule 35 mandates contract management plan with KPIs.", None),
    ("contracts", "contracts[].implementation.transactions[]", "array", None, "Rule 36 — prompt payment, Rule 44 — eInvoicing",
     "Rule-mandated", "Payment transactions. Rule 36 mandates 95% of invoices paid within 5/10 business days; quarterly reporting to MBIE. Rule 44 mandates Peppol eInvoicing capability by 2026/2027.", None),
    ("contracts", "contracts[].implementation.metrics[]", "array", None, "Rule 35(3)(a)",
     "Rule-mandated", "Performance metrics monitoring. Rule 35 mandates 'sufficient monitoring of contracts to ensure that commitments made in contracts are delivered and reported on'.", None),
    ("contracts", "contracts[].amendments[]", "array", None, None, "Gap",
     "Contract variations. GMC Variation templates exist (NZGP A-GMT) but no central publication.", None),
    # ── v0.4: extension fields on contracts ───────────────────────────────────
    ("contracts", "contracts[].contractingModel (ext)", "string", "(derived from contract template used: GMC vs Outcome Agreement vs Lite)", "Rule 10; Glossary 'relational contract', 'social investment outcomes contract'",
     "NZ Extension", "Contract structure: standard / outcomes-based-relational / lean-agile / commissioning / social-investment-outcomes / collaborative-contract.", "nz-contracting-model"),
    ("contracts", "contracts[].cmsFields (ext)", "object", "(from agency Contract Management System)", "Rule 34",
     "NZ Extension", "Mirrors Rule 34's 9 mandatory CMS fields: supplier name, NZBN, copy location, senior responsible officer, commercial support contact, supplier contact, dates, actual spend.", "nz-contract-management-system"),
    ("contracts", "contracts[].promptPayment (ext)", "object", "Rule 36 quarterly returns to MBIE (already public)", "Rule 36; Glossary 'electronic invoicing'",
     "NZ Extension", "On-time-payment % + period (quarterly) + target (95% from 1 Jan 2026) + payment-rule reference. Already publicly reported per Rule 36.", "nz-prompt-payment"),

    # ── relatedProcesses (panel relationships)
    ("relatedProcesses", "relatedProcesses[].id", "string", None, None, "Template-sourced", None, None),
    ("relatedProcesses", "relatedProcesses[].relationship", "array", None, "Rule 22 — Panel of suppliers",
     "Vocab Translation", "Panel parent → 'framework'; secondary procurement under panel → 'subcontract' or 'callOff'.", None),
    ("relatedProcesses", "relatedProcesses[].title", "string", None, None, "Template-sourced", None, None),
    ("relatedProcesses", "relatedProcesses[].identifier", "string", None, None, "Direct",
     "Reference to parent contract / panel ID.", None),

    # ── bids
    ("bids", "bids.statistics[]", "array", None, "Rule 30, Rule 33 — debrief", "Gap",
     "Bid statistics not published. Some bid data exists (debrief content per Rule 33) but is commercial-in-confidence under Rule 5.", None),
]


def build_mapping_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("OCDS Mapping")
    headers = ["OCDS Section", "OCDS Path", "Type", "GETS Source", "Rule Reference", "Status", "Notes", "NZ Extension ID"]
    widths = [14, 50, 12, 30, 30, 18, 70, 22]
    apply_header(ws, 1, headers, widths)

    for i, (section, path, typ, gets, rule, status, notes, ext) in enumerate(MAPPINGS, start=2):
        write_row(ws, i, [section, path, typ, gets or "—", rule or "—", status, notes or "", ext or ""])
        # Colour the status cell
        c = ws.cell(row=i, column=6)
        if status in STATUS_COLOURS:
            c.fill = PatternFill(start_color=STATUS_COLOURS[status], end_color=STATUS_COLOURS[status], fill_type="solid")
            c.font = Font(bold=True, color="FFFFFF", size=10)
            c.alignment = Alignment(horizontal="center", vertical="center")


# ── Sheet 3: Vocab Translations ──────────────────────────────────────────────

VOCAB = [
    # (OCDS field, GETS value(s), OCDS code, codelist file, notes)
    # Codelist files validated against open-contracting/standard 1.2-dev
    # v0.3: practitioner-corrected. Competition_Type is primary signal; RFx_Type → procurementMethodDetails.
    ("tender.procurementMethod", "Competition_Type='Open Competition' (any RFx_Type)", "open", "method.csv",
     "Openly advertised; any qualified supplier may submit. RFx_Type (RFT/RFP/RFQ) is captured in procurementMethodDetails as free text."),
    ("tender.procurementMethod", "Multi-step: ROI followed by RFP/RFT", "selective", "method.csv",
     "Open ROI advertised; shortlist selected; closed RFP/RFT to shortlist. Modelled as ONE OCID with stage transitions via release tags."),
    ("tender.procurementMethod", "Competition_Type='Closed Competition' from Panel of Suppliers (Rule 22/23)", "selective", "method.csv",
     "Pre-qualified suppliers list — selection happens before tender. Use nz-secondary-procurement extension to flag panel call-off."),
    ("tender.procurementMethod", "Competition_Type='Closed Competition' with Rule 12 exemption (Limited Competition)", "limited", "method.csv",
     "Direct invitation to a small number of known suppliers for technical or other Appendix 2 reasons."),
    ("tender.procurementMethod", "Award Notice with Rule 12 exemption (single supplier)", "direct", "method.csv",
     "Direct sourcing under Rule 12 + Appendix 2 — see nz-exemption-rationale extension."),
    ("tender.procurementMethodDetails", "Request for Tender (RFT)", "(free text — preserve verbatim)", "(no codelist)",
     "Glossary: clearly defined goods/services with technical requirements."),
    ("tender.procurementMethodDetails", "Request for Proposal (RFP)", "(free text — preserve verbatim)", "(no codelist)",
     "Glossary: open to innovative ways to achieve outcome."),
    ("tender.procurementMethodDetails", "Request for Quote (RFQ)", "(free text — preserve verbatim)", "(no codelist)",
     "Glossary: off-the-shelf goods/services where price is most important."),
    ("tender.procurementMethodDetails", "Registration of Interest (ROI) / Expression of Interest", "(free text — preserve verbatim)", "(no codelist)",
     "Glossary: also known as Expression of Interest. First formal stage of multistep tender process."),
    ("tender.procurementMethodDetails", "Competitive Dialogue", "(free text — preserve verbatim)", "(no codelist)",
     "Glossary (Rule 10): structured dialogue phase with shortlisted suppliers; suppliers often paid for participation."),
    ("tender.procurementMethodDetails", "Lean Agile Procurement (LAP)", "(free text — preserve verbatim)", "(no codelist)",
     "Glossary (Rules 10, 17): Big Room Event with shortlist; 2-3 day collaborative event."),
    ("tender.procurementMethodDetails", "Request for Information (RFI)", "(N/A — not a Notice of Procurement)", "(no codelist)",
     "Glossary: market research tool only. NOT a Notice of Procurement; must NOT be used to select/shortlist. Don't emit OCDS tender release."),
    ("parties[].roles", "'provider' (social services sector terminology)", "supplier", "partyRole.csv",
     "Glossary: 'Synonymous with supplier, frequently used in the social services sector.' Map to supplier role."),
    ("classification.scheme", "GETS 'tender watch codes'", "UNSPSC", "classificationScheme.csv",
     "Glossary: 'Codes used on GETS to classify goods, services and works. They are based on the United Nations Standard Products and Services Code (UNSPSC).'"),
    ("tender.status", "Pre-publication", "planning", "tenderStatus.csv", None),
    ("tender.status", "Published, awaiting Open Date", "planned", "tenderStatus.csv", None),
    ("tender.status", "Open Date passed AND Close Date in future", "active", "tenderStatus.csv", None),
    ("tender.status", "Close Date passed + Award Type Awarded", "complete", "tenderStatus.csv", None),
    ("tender.status", "Close Date passed + Award Type Not Awarded", "unsuccessful", "tenderStatus.csv", None),
    ("tender.status", "Tender withdrawn before close", "withdrawn", "tenderStatus.csv",
     "Use 'withdrawn' (1.2-dev) when supplier or buyer cancels before close. 'cancelled' for buyer-side cancellation."),
    ("tender.status", "Tender cancelled by buyer", "cancelled", "tenderStatus.csv",
     "Not currently distinguishable in GETS data without explicit cancellation flag."),
    ("awards[].status", "Award Type 'Awarded'", "active", "awardStatus.csv", None),
    ("awards[].status", "Award Type 'Not Awarded'", "unsuccessful", "awardStatus.csv", None),
    ("awards[].status", "Awaiting confirmation", "pending", "awardStatus.csv",
     "GETS doesn't model this stage; rare in practice."),
    ("awards[].status", "Award rescinded", "cancelled", "awardStatus.csv",
     "Not directly captured; would require monitoring award notice retraction."),
    ("tag (release type)", "GETS publishes a tender notice", "tender", "releaseTag.csv", None),
    ("tag (release type)", "GETS publishes Future Procurement Opportunity (Rule 37)", "planning",
     "releaseTag.csv", "Rule 37 FPOs are the closest GETS analogue to OCDS planning releases."),
    ("tag (release type)", "GETS publishes award notice (Award Type=Awarded)", "award",
     "releaseTag.csv", "Award notices in GETS carry tender data; emit release with tags=['tender','award'] if both stages are published in the same notice."),
    ("tag (release type)", "GETS publishes award notice (Award Type=Not Awarded)", "awardCancellation",
     "releaseTag.csv", "OCDS distinguishes unsuccessful tender (tenderStatus='unsuccessful') from cancelled award."),
    ("tag (release type)", "Material change after publication", "tenderAmendment", "releaseTag.csv",
     "Rule 21 — Changes to process or requirements."),
    ("tag (release type)", "Contract signed (post-award)", "contract", "releaseTag.csv",
     "Rule 32 mandates contract award notice within 30 business days of signing."),
    ("parties[].roles", "Posting Agency", "buyer, procuringEntity", "partyRole.csv",
     "Both roles apply to NZ posting agencies (they buy and they procure)."),
    ("parties[].roles", "Awarded Supplier", "supplier, tenderer", "partyRole.csv", None),
    ("parties[].roles", "Unsuccessful tenderer (debrief)", "tenderer", "partyRole.csv",
     "Rule 30/33 debrief recipients. Rule 5 protects detailed bid content."),
    ("parties[].roles", "Third-party agent acting for buyer", "procurementServiceProvider", "partyRole.csv",
     "Rule 13 — Third-party agents."),
    ("parties[].address.countryName", "Region = 'International'", "(actual country from address)", "country.csv",
     "GETS Region 'International' indicates non-NZ delivery; party country may still be NZ. Use ISO 3166-1 alpha-2 codes per OCDS."),
    ("currency (all values)", "(no GETS field)", "NZD", "currency.csv",
     "Hardcoded — GETS doesn't carry currency. ISO 4217."),
    ("language", "(no GETS field)", "en", "language.csv",
     "English assumed; Te Reo (mi) carried via nz-te-reo-names extension."),
    ("relatedProcesses[].relationship", "Tender Coverage = 'All of Government'", "framework",
     "relatedProcess.csv", "AoG panel parent. Per Rule 38."),
    ("relatedProcesses[].relationship", "Secondary procurement under AoG panel", "framework",
     "relatedProcess.csv", "Call-offs reference the framework via relatedProcesses with relationship=['framework']."),
    ("relatedProcesses[].relationship", "Subcontract under prime contract", "subContract",
     "relatedProcess.csv", "Rule 31 — Subcontracting."),
    ("relatedProcesses[].relationship", "Renewal of an expiring contract", "renewalProcess",
     "relatedProcess.csv", "Use when a procurement is the renewal of an expiring contract."),
    ("relatedProcesses[].relationship", "Earlier (unsuccessful) attempt at same procurement", "prior",
     "relatedProcess.csv", "Per Appendix 2.2 — re-procurement after open process produced no responses."),
    ("submissionMethod[]", "GETS website", "electronicSubmission", "submissionMethod.csv", None),
    ("submissionMethod[]", "Physical/postal address only", "written", "submissionMethod.csv", None),
    ("submissionMethod[]", "Rule 24 e-auction", "electronicAuction", "submissionMethod.csv", None),
    ("initiationType", "All GETS-sourced", "tender", "initiationType.csv",
     "Only 'tender' is currently in the OCDS initiationType codelist."),
]


def build_vocab_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("Vocab Translations")
    headers = ["OCDS Field", "GETS Value(s)", "OCDS Code", "Codelist File", "Codelist Source URL", "Translation Notes / Defensibility"]
    widths = [30, 48, 28, 22, 60, 60]
    apply_header(ws, 1, headers, widths)
    for i, row in enumerate(VOCAB, start=2):
        # row = (field, gets_val, ocds_code, codelist_file, notes)
        field, gets_val, ocds_code, codelist_file, notes = row
        url = f"{CODELIST_BASE}/{codelist_file}" if codelist_file else ""
        write_row(ws, i, [field, gets_val, ocds_code, codelist_file or "—", url, notes or ""])


# ── Sheet 4: NZ Extensions ───────────────────────────────────────────────────

EXTENSIONS = [
    # (id, target_object, fields, source_rule, rationale)
    ("nz-te-reo-names", "Organization, Item, Document",
     "{en: string, mi: string} on name fields",
     "Rule 1 — Treaty of Waitangi / Te Tiriti o Waitangi",
     "Bilingual name carriage. MBIE's own GETS schema flags Te Reo macron rendering as broken; "
     "this extension fixes it as a publication-time concern. Aligns with Government Procurement Charter."),
    ("nz-tender-coverage", "Tender",
     "{coverage: 'all-of-government' | 'common-capability' | 'syndicated' | 'sole-agency' | 'on-behalf'}",
     "Rules 38 (AoG), 39 (Common Capability), 40 (Syndicated), 22 (Panel)",
     "GETS Tender Coverage field captures procurement collaboration mechanism. No direct OCDS analogue. "
     "Maps cleanly to OCDS relatedProcesses where appropriate."),
    ("nz-agency-tier", "Organization (where role=buyer)",
     "{tier: 'public-service' | 'public-sector' | 'state-sector' | 'state-services' | 'crown-agent' | 'independent-crown-entity' | 'autonomous-crown-entity' | 'crown-research-institute' | 'district-health-board' | 'state-owned-enterprise' | 'territorial-authority' | 'tertiary-education-institution' | 'school-board-of-trustees' | 'other'}",
     "Application of Rules — Part Four; Glossary entries 'public sector', 'public service', 'state sector', 'state services'",
     "v0.3: aligned to the four formal taxonomies in the Rules glossary. "
     "public-service = Schedule 1 of State Sector Act 1988 (departments + ministries). "
     "public-sector = broadest (includes Regional Councils + Territorial Authorities). "
     "state-sector = middle scope (includes State-owned enterprises + Tertiary Education Institutes). "
     "state-services = Schedule 4/4A of Public Finance Act + Crown agents/entities + CRIs + Reserve Bank + School Boards."),
    ("nz-mandate-level", "Organization (where role=buyer)",
     "{mandateLevel: 'mandated' | 'expected' | 'encouraged'}",
     "Application of Rules — Part Four (sections A and B)",
     "Which compliance tier of the Rules applies to the agency. Mandated agencies (Public Service depts, "
     "Police, NZDF, Crown agents, ICEs, ACEs, CECs, CRIs) must apply; School Boards and PFA Sch4 expected; "
     "wider state sector encouraged."),
    ("nz-economic-benefits", "Tender, Award",
     "{benefits: [{category, weighting, description}], minimumWeighting: 0.10, scope: 'NZ' | 'ANZ'}",
     "Rule 8 — Economic benefit to NZ; Glossary 'New Zealand business'",
     "Mandatory ≥10% evaluation weighting for procurements over the value threshold. Categories per Rule 8(4): "
     "workforce / SMEs / exports / industry capability / innovation / sustainability / social-cultural outcomes. "
     "Rule 8(5)(d) requires contract provisions to deliver agreed economic benefits. "
     "v0.3: Trans-Tasman scope flag — per the glossary, 'New Zealand business' for Rule 8 purposes formally INCLUDES Australian business."),
    ("nz-opt-out-rationale", "Tender",
     "{rationale: <enum>, justification: string}",
     "Rule 11, Rule 32(2)(h), Appendix 1",
     "13 valid opt-out reasons in Appendix 1 (between-agency, overseas, non-contractual, land/buildings, "
     "conditional grant, international development assistance, public services, central financial control, "
     "military/security). Rule 32(2)(h) requires justification in award notice."),
    ("nz-exemption-rationale", "Tender",
     "{exemption: <enum>, justification: string}",
     "Rule 12, Rule 32(2)(h), Appendix 2",
     "10 valid exemptions in Appendix 2 (emergency, post-open-process re-procurement, only-one-supplier, "
     "judicial order, additional goods/services, prototype, commodity market, exceptionally advantageous, "
     "design contest, market-led proposal). Rule 32(2)(h) requires justification."),
    ("nz-prequalification", "Tender",
     "{prequalificationRequired: boolean, prequalificationScheme: string}",
     "Rule 23, Rule 17(2)(i)",
     "Prequalification required field plus the specific scheme (e.g. SICP for ICT). "
     "Rule 14 pre-conditions are separate but related."),
    ("nz-prompt-payment", "Contract.implementation",
     "{onTimePercentage: number, period: 'quarter', target: 0.95, paymentRule: 'Rule 36'}",
     "Rule 36 — Prompt payment times",
     "From 1 Jan 2026, agencies must pay 95% of domestic trade invoices within 5 business days (eInvoice) "
     "or 10 business days (other). Quarterly publication to MBIE is mandatory. Already public — extension "
     "structures the existing data."),
    ("nz-einvoicing-capability", "Organization (where role=buyer)",
     "{peppolCapable: boolean, peppolID: string, capabilityDate: string}",
     "Rule 44 — eInvoicing capability",
     "From 1 Jan 2026 agencies receiving 2,000+ trade invoices annually must be Peppol-capable. "
     "Significant for cross-border interop with Australia (joint Peppol commitment)."),
    ("nz-contract-management-system", "Contract",
     "Mirrors Rule 34(2) mandatory CMS fields: supplier name, NZBN, location of contract copy, "
     "senior responsible officer, commercial support contact, supplier contact, dates, actual spend",
     "Rule 34 — Contract Management System",
     "Rule 34 mandates 9 fields per contract in agency CMS. None centrally published today. "
     "Each maps cleanly to existing OCDS contracts.* paths but the extension formalises the obligation."),
    ("nz-broader-outcomes", "Tender, Award, Contract",
     "{outcomes: ['waste-reduction' | 'living-wage' | 'maori-business' | 'pasifika-business' | 'regional' | 'apprenticeships' | ...]}",
     "Rule 8(4), Government Procurement Charter, broader outcomes framework",
     "NZ-specific procurement priorities/outcomes that influence award. Cabinet has set specific broader-outcomes "
     "policies (Living Wage, Māori-Pasifika business, etc.) that are mandatory for some procurements."),
    ("nz-gets-source", "any",
     "{source: 'gets', getsId: string, getsUrl: string}",
     "Rule 17, Rule 32 (publish on GETS), Rule 37 (FPOs on GETS)",
     "Provenance back to the original GETS notice. Probity/lineage trail."),
    ("nz-nzbn-resolver", "Organization",
     "{nzbnResolved: boolean, nzbnLegalName: string, nzbnEntityType: string}",
     "Rule 17 'should request NZBN', Rule 32(2)(i) 'NZBN where available', Rule 34(2)(b) 'NZBN or another unique identifier'",
     "NZBN-validated party resolution. MBIE's own schema notes NZBN field is not validated; "
     "resolving via the Companies Office NZBN registry adds substantial value."),
    # ── v0.3 NEW EXTENSIONS ──────────────────────────────────────────────
    ("nz-treaty-of-waitangi-exception", "Tender, Award",
     "{treatyExceptionInvoked: boolean, rationale: string, internationalAgreement: string}",
     "Rule 1 (Principles, Te Tiriti o Waitangi anchor); Government Procurement Charter; "
     "Glossary: 'Te Tiriti o Waitangi/Treaty of Waitangi Exception'",
     "★ NZ-specific. NZ is party to international agreements with FORMAL Te Tiriti o Waitangi exceptions for "
     "Māori-favourable measures. Distinct from Rule 11 opt-out and Rule 12 exemption — invoked under international "
     "trade agreement provisions. Procurements invoking this exception need an extension field documenting "
     "the rationale and which agreement provides the exception."),
    ("nz-procurement-method-detail", "Tender",
     "{detail: 'single-stage-rft' | 'single-stage-rfp' | 'single-stage-rfq' | 'multi-step-roi-rfp' | 'multi-step-roi-rft' | 'competitive-dialogue' | 'lean-agile-procurement' | 'panel-secondary-procurement' | 'direct-from-panel' | 'rule-12-exempt'}",
     "Rule 10 enumeration of compliant approaches; Glossary: 'multi-step process', 'competitive dialogue', "
     "'lean agile procurement (LAP)', 'Registration of Interest', 'Request for Proposal', 'Request for Tender', "
     "'Request for Quote'",
     "Sub-typing within the OCDS procurementMethod codelist. OCDS core has only 4 method codes (open/selective/limited/direct); "
     "this extension preserves NZ-specific method detail. Anchored to Rule 10's full enumeration of permitted approaches "
     "(page 28) and the glossary's formal definitions of each method."),
    ("nz-contracting-model", "Contract, Tender",
     "{model: 'standard' | 'outcomes-based-relational' | 'lean-agile' | 'commissioning' | 'social-investment-outcomes' | 'collaborative-contract'}",
     "Rule 10 enumeration of compliant approaches; Glossary: 'relational contract' (= outcomes-based), "
     "'social sector commissioning', 'social investment outcomes contract'",
     "Orthogonal to procurement method — captures the CONTRACT structure regardless of how supplier was selected. "
     "Glossary explicitly: relational contract = outcomes-based contract (collapsed into one value). "
     "Different from selection process — a relational/outcomes-based contract may be awarded via any procurement method."),
    ("nz-secondary-procurement", "Tender, Award",
     "{secondary: boolean, parentArrangement: 'all-of-government' | 'common-capability' | 'syndicated' | 'panel', "
     "parentRfxId: string}",
     "Rule 22 (Panel of suppliers); Rule 12 (referencing secondary procurement); Glossary: 'secondary procurement'",
     "Formal NZ term for panel call-offs. Glossary: 'Where an agency purchases goods, services or works from a "
     "Panel of Suppliers, an All-of-Government Contract, Common Capabilities Contract or Syndicated Contract.' "
     "Reinforces OCDS relatedProcesses[].relationship='framework' modelling but adds the NZ-specific call-off flag."),
]


def build_extensions_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("NZ Extensions")
    headers = ["Extension ID", "Target Object(s)", "Fields", "Source Rule(s)", "Rationale"]
    widths = [22, 28, 60, 32, 80]
    apply_header(ws, 1, headers, widths)
    for i, row in enumerate(EXTENSIONS, start=2):
        write_row(ws, i, list(row))


# ── Sheet 5: Rules Inventory ─────────────────────────────────────────────────

RULES = [
    # (number, title, OCDS-relevance summary)
    (1, "Principles and the Government Charter", "Anchors Te Tiriti / Treaty obligations — basis for nz-te-reo-names extension."),
    (2, "Integrity", "Probity foundation — citation lineage in OCDS supports this."),
    (3, "Transparency and Accountability", "Direct alignment with OCDS purpose."),
    (4, "Non-discrimination and offsets", "Constrains nz-economic-benefits design (must not discriminate by location/ownership)."),
    (5, "Protection of supplier information", "Defines what cannot be published — bid statistics commercially sensitive (limits OCDS bids[] coverage)."),
    (6, "Planning", "★ KEY. Mandates 12 planning elements — basis for nearly all OCDS planning section coverage."),
    (7, "Estimating monetary value", "★ KEY. Mandates value estimate in business case / procurement plan → planning.budget.amount."),
    (8, "Economic benefit to New Zealand", "★ KEY. ≥10% evaluation weighting; 7 benefit categories — basis for nz-economic-benefits + nz-broader-outcomes."),
    (9, "Planning for new construction works", "Construction-specific planning artefacts (DECA tool, capability assessments)."),
    (10, "Requirement to openly advertise", "Anchors tender.procurementMethod = 'open' default."),
    (11, "Opt-out procurements", "Basis for nz-opt-out-rationale extension; Appendix 1 codelist."),
    (12, "Exemption from open advertising", "Basis for nz-exemption-rationale extension; Appendix 2 codelist."),
    (13, "Third-party agents", "Affects parties[].roles — agent acting for buyer."),
    (14, "Pre-conditions", "Pre-conditions component of tender.eligibilityCriteria."),
    (15, "Technical specifications", "tender.documents[] component."),
    (16, "Sufficient time", "Constrains tender.tenderPeriod.endDate (minimum periods)."),
    (17, "Notice of Procurement", "★ KEY. 16 mandatory fields a-p — most align directly to OCDS tender.* fields."),
    (18, "Intellectual property", "tender extension — IP terms in NoP."),
    (19, "Responding to queries", "tender.hasEnquiries / enquiries[] coverage."),
    (20, "Additional information", "tender.documents[] amendments / addenda."),
    (21, "Changes to process or requirements", "tag = 'tenderAmendment'."),
    (22, "Panel of suppliers", "★ KEY for relatedProcesses extension — panel parent + secondary procurements."),
    (23, "Pre-qualified suppliers list", "Basis for nz-prequalification extension."),
    (24, "E-auction", "tender.submissionMethod = ['electronicAuction']."),
    (25, "Due diligence", "Captured in due diligence checklist template."),
    (26, "Managing National Security Risks", "Risk subtype for nz-risk-assessment extension."),
    (27, "Treatment of responses", "Internal to evaluation — limited OCDS exposure (Rule 5 protects responses)."),
    (28, "Reasons to exclude a supplier", "awards[].rationale where status=unsuccessful."),
    (29, "Awarding the contract", "Award-decision lifecycle — awards[].status transitions."),
    (30, "Informing suppliers of the decision", "tender.numberOfTenderers / awards[].suppliers[]."),
    (31, "Subcontracting", "Basis for nz-subcontractors extension; relatedProcesses for subcontract relationships."),
    (32, "Contract award notice", "★ KEY. 10 mandatory fields — GETS captures only ~6 of them. Compliance gap inside MBIE."),
    (33, "Debriefing suppliers", "Could feed bids.statistics but Rule 5 protects bid content."),
    (34, "Contract Management System", "★ KEY. 9 mandatory CMS fields — mirror to contracts[] section."),
    (35, "Contract Management Plan", "★ KEY. KPIs + monitoring — basis for contracts[].milestones[] and contracts[].implementation.metrics[]."),
    (36, "Prompt payment times", "★ KEY. Quarterly publication mandatory — basis for nz-prompt-payment extension. Already public."),
    (37, "Future Procurement Opportunities", "★ KEY. FPOs published on GETS — direct mapping to tag='planning'."),
    (38, "All-of-Government contracts", "Basis for relatedProcesses (framework / callOff) and nz-tender-coverage='all-of-government'."),
    (39, "Common Capability contracts", "nz-tender-coverage='common-capability'."),
    (40, "Syndicated contracts", "nz-tender-coverage='syndicated' (Open or Closed)."),
    (41, "Infrastructure", "Treasury / NIFFC / Crown Infrastructure Delivery interactions — separate object stream."),
    (42, "Business cases and investment decisions", "planning.documents[] = business case; Treasury Better Business Case framework."),
    (43, "Investment reviews", "planning.documents[] additional artefacts."),
    (44, "eInvoicing capability", "★ KEY. Peppol mandate — basis for nz-einvoicing-capability extension. Aligns with Australia."),
    (45, "Reporting", "Procurement System Leader monitoring — meta-level; underpins legal authority for OCDS publication."),
    (46, "Maintaining records", "3-year retention minimum — supports OCDS historical depth requirement."),
    (47, "Approved Government Model Templates", "★ KEY. Mandatory A-GMT use — every template field becomes a candidate OCDS source."),
]


def build_rules_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("Rules Inventory")
    headers = ["Rule #", "Title", "OCDS-Relevance"]
    widths = [8, 42, 100]
    apply_header(ws, 1, headers, widths)
    for i, row in enumerate(RULES, start=2):
        write_row(ws, i, list(row))


# ── Sheet 6: Templates Inventory ─────────────────────────────────────────────

TEMPLATES = [
    # (category, name, mandatory?, OCDS-relevant fields, notes)
    ("Procurement Plan", "Extra lite procurement plan ($5k-$50k)", "Encouraged",
     "planning.rationale, planning.budget.amount, market analysis (extension), risk (extension)",
     "Below value threshold; agencies expected to apply good practice."),
    ("Procurement Plan", "Lite procurement plan ($50k-$100k)", "Encouraged",
     "planning.rationale, planning.budget.amount, planning.milestones",
     "Below value threshold."),
    ("Procurement Plan", "Procurement plan (>$100k)", "Mandatory (above threshold)",
     "All planning.* fields; Rule 6's 12 elements; Rule 7 value estimate; Rule 8 economic benefits",
     "★ Primary source for OCDS planning section."),
    ("Procurement Policy", "How to write a procurement policy template", "Encouraged",
     "Agency-level meta — feeds buyer.details.policies extension if added",
     "Strategic-level, not per-procurement."),
    ("RFx Notice", "Advance Notice", "Optional",
     "tender.tenderPeriod (intent), tender.title, tender.description (early)",
     "Pre-tender advance warning. Could emit early planning release."),
    ("RFx", "Request for Information (RFI)", "Optional (market research)",
     "Not a tender — Rule 17 explicitly says RFI is not a Notice of Procurement",
     "Don't emit OCDS tender release for RFIs. Could be a separate research artefact."),
    ("RFx", "Registration of Interest (ROI)", "Optional (multi-step)",
     "tender (first stage), tag='tender'",
     "First step in multi-step process. Use OCDS multi-stage modelling."),
    ("RFx", "Request for Proposal (RFP)", "Mandatory A-GMT for low-value/risk",
     "All tender.* mandatory fields per Rule 17",
     "Maps to procurementMethod='selective' (interpretive)."),
    ("RFx", "Request for Quote (RFQ-L) Lite", "Mandatory A-GMT",
     "All tender.* mandatory fields per Rule 17",
     "Very low-value. Maps to procurementMethod='limited'."),
    ("RFx", "Request for Quote (RFQ)", "Mandatory A-GMT",
     "All tender.* mandatory fields per Rule 17",
     "Medium-high value/risk RFQ. Maps to procurementMethod='limited'."),
    ("RFx Terms", "ROI / RFP / RFQ terms and conditions", "Mandatory (with corresponding RFx)",
     "tender.documents[] reference",
     "Standardised — could be a single OCDS document with stable URL."),
    ("RFx Response", "RFx response form templates (RFI / ROI / RFP / RFQ)", "Mandatory",
     "Bid responses — Rule 5 protects content (commercial-in-confidence)",
     "Limits bids[] coverage in OCDS."),
    ("Evaluation", "Evaluation panel instructions / minutes / recommendation", "Encouraged",
     "tender.awardCriteria documentation",
     "Internal evaluation records. Per Rule 46 retention."),
    ("Evaluation", "Tender criteria evaluation form", "Encouraged",
     "tender.awardCriteria, tender.awardCriteriaDetails",
     "Captures weightings and methodology."),
    ("Due diligence", "Due diligence checklist", "Encouraged (Rule 25)",
     "Internal record — feeds awards[].suppliers vetting outcome",
     "Not directly published."),
    ("Negotiation", "Negotiation plan / checklist", "Encouraged",
     "Internal record",
     "Pre-award negotiation artefact. Rule 5 protects content."),
    ("Contract", "Government Model Contract — Form 1 (Crown) Goods", "Mandatory A-GMT (Rule 47)",
     "★ Primary source for contracts.* section. Schedule 2 carries specifics.",
     "Crown agencies (Public Service depts etc.)."),
    ("Contract", "Government Model Contract — Form 1 (Crown) Services", "Mandatory A-GMT", "Same", "Crown."),
    ("Contract", "Government Model Contract — Form 2 (non-Crown) Goods", "Mandatory A-GMT", "Same", "Non-Crown buyers (councils, SOEs)."),
    ("Contract", "Government Model Contract — Form 2 (non-Crown) Services", "Mandatory A-GMT", "Same", "Non-Crown buyers."),
    ("Contract", "GMC Contract Variation — Goods/Services", "Mandatory A-GMT for amendments",
     "contracts[].amendments[] basis",
     "Currently no central publication of variations."),
    ("Contract", "GMC Lite contract", "Mandatory A-GMT for very-low-value", "contracts[].* (subset)",
     "Streamlined fields for sub-$50k goods/services."),
    ("Contract Mgmt", "Contract register template (XLSX)", "Encouraged (Rule 34 'systematic approach')",
     "★ Mirrors Rule 34's 9 mandatory CMS fields → contracts.* section",
     "Standard register format. Easy candidate for ingestion if agencies share."),
    ("Contract Mgmt", "Contract management plan template", "Mandatory (Rule 35)",
     "contracts[].milestones, contracts[].implementation.metrics",
     "★ Source for contract performance KPIs."),
    ("Contract Mgmt", "Lite contract management plan", "Mandatory for lower-value/complexity (Rule 35)", "Same", None),
    ("Contract Mgmt", "Relationship and contract management essential task register", "Encouraged",
     "contracts[].implementation activities", None),
    ("Social Service", "Outcome agreement (bilateral / integrated)", "Specialised contract template",
     "contracts.* with social-outcome focus", "Rule 17 references social investment outcomes contracts."),
    ("Construction", "DECA tool, asset/client/market/sponsor capability assessments", "Encouraged (Rule 9)",
     "Construction-specific risk assessment", "Feeds nz-risk-assessment extension."),
    ("Construction", "Risk register template", "Encouraged",
     "contracts[].risks[] (extension)", None),
    ("SRM", "Supplier segmentation / category segmentation tools", "Encouraged",
     "Cross-procurement supplier intelligence", "Long-term Project Unify value-add territory."),
    ("SRM", "Balanced scorecard / service improvement plan templates", "Encouraged",
     "Performance metrics over time",
     "contracts[].implementation tracking — long-term performance signal."),
]


def build_templates_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("Templates Inventory")
    headers = ["Category", "Template Name", "Mandate Level", "OCDS-Relevant Fields", "Notes"]
    widths = [16, 50, 28, 60, 50]
    apply_header(ws, 1, headers, widths)
    for i, row in enumerate(TEMPLATES, start=2):
        write_row(ws, i, list(row))


# ── Sheet 7: Publishing Governance (NZ-localised from NSW Open Data Guidelines) ─

# Adapted from NSW Government Open Data Publishing Guidelines V3.0 (Nov 2022),
# localised to NZ context (OIA in place of GIPA, NZGP/MBIE roles, OCDS-specific concerns).

GOVERNANCE_STEPS = [
    # (step, name, what's approved, role responsible, NZ-OCDS specifics)
    (1, "Collect & Create",
     "GETS data ingestion + OCDS schema",
     "Data Custodian (Project Unify) + Legal Advisor",
     "Confirm GETS data is genuinely public (it is — published on gets.govt.nz). "
     "Document the ingestion pipeline (Pipeline Builder visual lineage satisfies this)."),
    (2, "Understand & Profile",
     "Field-level profile + completeness analysis",
     "Subject Matter Expert (procurement domain)",
     "v0.1+ mapping spreadsheet IS this artefact. "
     "Profile coverage: 23 Direct + 13 Derived + 19 Rule-mandated + 14 Template-sourced + 14 NZ Extensions + 8 Constants + 3 Vocab Translations + 3 Gaps."),
    (3, "Classify",
     "Sensitivity classification per field/object",
     "Data Custodian + (where applicable) GIPA-equivalent / OIA officer",
     "See Sensitivity Classification sheet. NZ Rule 5 (Protection of supplier information) "
     "is the primary anchor. Public Interest test applies under OIA s9."),
    (4, "Approve",
     "Authorisation to publish OCDS releases",
     "Data Authority (Project Unify lead) — pre-launch: OCP Helpdesk technical sign-off + Transparency NZ civil-society review",
     "Pre-launch checklist: schema valid via ocdskit, mapping reviewed externally, lineage trail visible, NZ extensions documented."),
    (5, "Define Methodology & Document",
     "Publication methodology, frequency, format, metadata",
     "Data Custodian",
     "Frequency: real-time append on each new GETS notice (daily batch acceptable for v1). "
     "Format: OCDS 1.1.5 JSON + JSON Lines for bulk + CSV for accessibility. "
     "Stable URL pattern: data.projectunify.nz/ocds/releases/{date}.json + /index.json."),
    (6, "Design & Test",
     "End-to-end pipeline + ocdskit validation",
     "Business System Owner (Foundry pipeline lead)",
     "Test cases: (a) golden tender from each RFx type; (b) cancelled tender; (c) award + Not Awarded; "
     "(d) NSW-style edge cases (malformed postcode, duplicate tenderers, embedded amount in Comments). "
     "ocdskit validate must pass for every release before publication."),
    (7, "Prepare & Publish",
     "Public release files + documentation site",
     "Data Custodian",
     "Submit to OCP Data Registry once stable. Publish field-level mapping doc as machine-readable artefact "
     "alongside the data (NSW's failure mode: documented their data but never their mapping)."),
    (8, "Monitor & Maintain",
     "Quality, refresh cadence, schema drift",
     "Data Custodian + Subject Matter Expert quarterly",
     "Critical lesson from NSW: their OCDS publication is 'no longer updated by the publisher'. "
     "Foundry's automated pipeline removes the manual maintenance burden. "
     "Quarterly schema-drift check + annual review of NZ Extensions vs Rule changes."),
]


GOVERNANCE_ROLES = [
    ("Data Custodian", "Project Unify lead",
     "Owns the operational publication pipeline and dataset quality. "
     "Equivalent: NSW Data Custodian; UK Cabinet Office Data Owner."),
    ("Data Authority", "Project Unify lead (initially) → migrate to NZGP/MBIE upon adoption",
     "Approves what gets published. Pre-NZGP-adoption: Project Unify acts in this role with OCP/Transparency NZ as external check. "
     "Post-adoption: NZGP Procurement Strategy team."),
    ("Subject Matter Expert", "Procurement domain practitioner",
     "Validates field interpretations match real procurement practice. "
     "Engage via Transparency NZ network or via direct relationship with a friendly buyer agency."),
    ("Legal Advisor", "Reviewing counsel familiar with OIA, Privacy Act 2020, Rule 5",
     "Required before any first publication. Confirms public-interest test, Privacy Act compliance, no third-party rights."),
    ("OIA Officer (where applicable)", "Equivalent of NSW GIPA officer",
     "If working with an agency on agency-supplied data, the agency's OIA officer reviews releases."),
    ("OCP Helpdesk", "open-contracting.org technical reviewer",
     "External technical validator. Free service. Their endorsement is the credibility lever."),
    ("Civil Society Reviewer", "Transparency NZ + named NZ academic + named NZ data journalist",
     "Independent review of utility and accessibility. Addresses NZ0029 IRM finding that civil society participation "
     "must be 'systematically included'."),
    ("Business System Owner", "Foundry pipeline engineer",
     "Operational owner of the Pipeline Builder transforms + ontology + ocdskit validation. "
     "Maintains the lineage trail."),
]


def build_governance_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("Publishing Governance")
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 38
    ws.column_dimensions["D"].width = 50
    ws.column_dimensions["E"].width = 80

    # Title block
    ws.cell(row=1, column=1, value="NZ-OCDS Publishing Governance").font = Font(bold=True, size=14)
    ws.cell(row=2, column=1, value="Adapted from NSW Government Open Data Publishing Guidelines V3.0 (Nov 2022). NZ-localised: OIA in place of GIPA; NZGP/MBIE in place of NSW DCS; OCDS-specific concerns layered in.").font = Font(italic=True, size=10, color="6B7280")
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells("A2:E2")
    ws.row_dimensions[2].height = 30

    # Section: 8-step process
    section = ws.cell(row=4, column=1, value="The 8-step publishing process")
    section.font = SECTION_FONT
    section.fill = SECTION_FILL
    ws.merge_cells("A4:E4")

    headers = ["#", "Step", "What is approved/produced", "Role responsible", "NZ-OCDS specifics"]
    widths = [4, 28, 38, 50, 80]
    apply_header(ws, 5, headers, widths)
    for i, row in enumerate(GOVERNANCE_STEPS, start=6):
        write_row(ws, i, list(row))

    # Section: Roles
    role_start = 6 + len(GOVERNANCE_STEPS) + 2
    section = ws.cell(row=role_start, column=1, value="Roles & responsibilities")
    section.font = SECTION_FONT
    section.fill = SECTION_FILL
    ws.merge_cells(f"A{role_start}:E{role_start}")

    role_headers = ["Role", "Holder (initially)", "Responsibility / Notes"]
    role_widths = [30, 50, 80]
    # Apply header at role_start+1
    for i, h in enumerate(role_headers, start=1):
        c = ws.cell(row=role_start + 1, column=i, value=h)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = BORDER

    for i, row in enumerate(GOVERNANCE_ROLES, start=role_start + 2):
        for j, v in enumerate(row, start=1):
            c = ws.cell(row=i, column=j, value=v)
            c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            c.border = BORDER
            c.font = Font(size=10)


# ── Sheet 8: Sensitivity Classification ──────────────────────────────────────
# Anchored to:
#  - NZ Rule 5 (Protection of supplier information)
#  - Official Information Act 1982 (s9 reasons for withholding)
#  - Privacy Act 2020
#  - NSW Information Classification Labelling and Handling Guidelines V2.3 (2021)

SENSITIVITY = [
    # (data_class, ocds_path, action, justification, reference)
    ("Personal information (individuals)",
     "parties[].contactPoint.name (where individual), parties[].contactPoint.email (personal)",
     "Suppress",
     "Privacy Act 2020 prohibits publishing personal information without lawful basis. Use generic role-based contacts (e.g. 'Procurement Team') instead.",
     "Privacy Act 2020 s22 (IPP 11); NSW IC Guidelines — Personal Information; NZGP Rule 5"),
    ("Health information",
     "Any field containing health-status references",
     "Suppress",
     "Higher protection threshold. Never publish.",
     "Health Information Privacy Code 2020"),
    ("Commercially sensitive — pricing structures",
     "bids[].statistics, awards[].value (when below threshold + identifies supplier margin), comments fields",
     "Aggregate or Suppress",
     "Rule 5 protects pricing structures, profit margins, market strategies. OIA s9(2)(b)(ii) protects 'commercial position of person who supplied it'.",
     "NZGP Rule 5; OIA 1982 s9(2)(b); NSW IC Guidelines — Business Confidentiality"),
    ("Commercially sensitive — trade secrets / know-how",
     "tender.documents[] (specifications), award.description (technical details)",
     "Redact",
     "Rule 5 explicit list includes 'trade secrets and know-how'.",
     "NZGP Rule 5(1); OIA s9(2)(b)(i)"),
    ("Bid content (unsuccessful)",
     "bids[].details, bids[].documents",
     "Suppress",
     "Rule 5 — design and content of a tender is commercially sensitive. Publishing unsuccessful bid content prejudices future supplier participation.",
     "NZGP Rule 5; Rule 33 (debrief) limits scope of disclosure"),
    ("Bid content (winning)",
     "awards[].documents (where they include bid content)",
     "Conditional publication",
     "Some elements (price, headline scope) become public via award notice (Rule 32). Detailed bid content remains protected unless supplier consented in NoP.",
     "NZGP Rule 5 + Rule 17(2)(n); OIA s9"),
    ("National security",
     "Any field on tenders covered by Rule 26",
     "Suppress (entire release)",
     "Tenders involving national security risks (Rule 26) should be excluded from public OCDS feed entirely. Redaction is insufficient — even metadata may be sensitive.",
     "NZGP Rule 26; OIA s6(a); NSW IC Guidelines — Crime/defence/intelligence"),
    ("Supplier identifiable information at low values",
     "parties[].name + parties[].address for sole-trader / small NZBN entities",
     "Conditional publication",
     "For small suppliers, public address may equal personal residence. Default: publish business address only. Don't publish full address unless supplier has consented (e.g. publicly listed contact).",
     "Privacy Act 2020 — re-identification risk; NSW IC Guidelines — Personal Information"),
    ("Information given in confidence under Rule 5(2)",
     "Any field marked 'commercial in confidence' in source NoP",
     "Suppress",
     "Rule 5(2)(c) explicitly allows limited disclosure only as expressly notified in NoP.",
     "NZGP Rule 5(2)"),
    ("Officials / public-facing roles",
     "parties[].contactPoint where role is published in agency directory",
     "Publish",
     "Public-facing officials' professional contact details are not personal information for OIA purposes.",
     "OIA s2(1) 'official information'; NSW IC Guidelines — Public Officials"),
    ("Information already in the public domain",
     "Title, Open Date, Close Date, awarded supplier name, award value (over threshold)",
     "Publish",
     "Already on GETS by mandate. OCDS publication is structuring, not re-disclosure.",
     "NZGP Rules 17, 32 — mandatory public notice fields"),
    ("Aggregate statistics derived from sensitive fields",
     "Calculated sums/averages across awards, supplier counts per agency etc.",
     "Publish (when sample size ≥ minimum)",
     "Aggregates with k-anonymity properties are publishable. Set k≥5 or higher per advice.",
     "NSW IC Guidelines — Business Impact Levels; OPC privacy guidance on de-identification"),
    ("Documents (NZGP A-GMTs & Schedule 2s)",
     "tender.documents[], contracts[].documents[]",
     "Publish (template document); redact (filled-in attachments)",
     "Standard A-GMT documents (Government Model Contracts, T&Cs) are public. Specific filled-in versions may contain sensitive fields — redact those before linking.",
     "NZGP Rule 47; Rule 5"),
    ("Subcontractor information",
     "Rule 31 disclosures",
     "Redact identifying details",
     "Rule 31 requires prime to disclose subcontractor info on request — but this is not the same as public publication. Treat as commercial in confidence by default unless supplier consents.",
     "NZGP Rule 31; Rule 5"),
]


SENSITIVITY_PROCESS = [
    ("1. Default: Open by default, protected as required",
     "Per NSW Open Data Policy + NZ OIA presumption in favour of disclosure (s5)."),
    ("2. Apply the public-interest test (OIA s9)",
     "For each field: balance the public interest in disclosure vs the protected interest. Document the conclusion."),
    ("3. Classify each OCDS field by sensitivity tier",
     "Use the table above. Default to 'Publish' unless explicitly listed as Redact / Aggregate / Suppress."),
    ("4. Where sensitivity = 'Conditional publication'",
     "Decision must be made per-procurement, not per-feed. Build the conditional logic into the Pipeline Builder transform."),
    ("5. Document every redaction/suppression in the release",
     "OCDS supports 'withheldInformation' arrays (or a parallel transparency log). Don't silently drop fields — declare them."),
    ("6. Publish a Sensitivity Statement alongside the feed",
     "Lists categories suppressed, redaction methodology, contact for OIA requests. NSW publishes equivalent guidance — emulate."),
    ("7. Annual review",
     "Re-evaluate classifications when Rules change, when OIA case law shifts, or when civil society raises specific concerns."),
]


def build_sensitivity_sheet(wb: openpyxl.Workbook) -> None:
    ws = wb.create_sheet("Sensitivity Classification")

    # Title block
    ws.cell(row=1, column=1, value="Sensitivity Classification — what to publish, redact, or suppress").font = Font(bold=True, size=14)
    ws.cell(row=2, column=1,
        value="Anchored to: NZGP Rule 5 (Protection of supplier information); Official Information Act 1982 (s9 reasons for withholding); Privacy Act 2020; NSW Government Information Classification Labelling and Handling Guidelines V2.3 (2021).").font = Font(italic=True, size=10, color="6B7280")
    ws.cell(row=2, column=1).alignment = Alignment(wrap_text=True)
    ws.merge_cells("A2:E2")
    ws.row_dimensions[2].height = 36

    # Process steps section
    section = ws.cell(row=4, column=1, value="Decision process")
    section.font = SECTION_FONT
    section.fill = SECTION_FILL
    ws.merge_cells("A4:E4")

    headers = ["Step", "Description"]
    widths = [40, 90]
    apply_header(ws, 5, headers, widths)
    for i, row in enumerate(SENSITIVITY_PROCESS, start=6):
        write_row(ws, i, list(row))

    # Classification table
    table_start = 6 + len(SENSITIVITY_PROCESS) + 2
    section = ws.cell(row=table_start, column=1, value="Field-level classification")
    section.font = SECTION_FONT
    section.fill = SECTION_FILL
    ws.merge_cells(f"A{table_start}:E{table_start}")

    cls_headers = ["Data class", "OCDS path(s) affected", "Action", "Justification", "Reference"]
    cls_widths = [38, 58, 22, 70, 50]
    apply_header(ws, table_start + 1, cls_headers, cls_widths)

    action_colours = {
        "Publish": "10B981",
        "Suppress": "EF4444",
        "Redact": "F59E0B",
        "Aggregate or Suppress": "F59E0B",
        "Conditional publication": "8B5CF6",
        "Suppress (entire release)": "991B1B",
        "Publish (when sample size ≥ minimum)": "10B981",
        "Publish (template document); redact (filled-in attachments)": "F59E0B",
        "Redact identifying details": "F59E0B",
    }

    for i, row in enumerate(SENSITIVITY, start=table_start + 2):
        write_row(ws, i, list(row))
        action = row[2]
        if action in action_colours:
            c = ws.cell(row=i, column=3)
            c.fill = PatternFill(start_color=action_colours[action], end_color=action_colours[action], fill_type="solid")
            c.font = Font(bold=True, color="FFFFFF", size=10)
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


# ── Build & save ─────────────────────────────────────────────────────────────

def main() -> None:
    wb = openpyxl.Workbook()
    build_readme(wb.active)
    build_mapping_sheet(wb)
    build_vocab_sheet(wb)
    build_extensions_sheet(wb)
    build_rules_sheet(wb)
    build_templates_sheet(wb)
    build_governance_sheet(wb)
    build_sensitivity_sheet(wb)

    wb.save(OUTPUT)
    print(f"Saved: {OUTPUT}")
    print(f"Sheets: {wb.sheetnames}")
    # Quick stats
    counts = {}
    for status in [m[5] for m in MAPPINGS]:
        counts[status] = counts.get(status, 0) + 1
    print("\nMapping status breakdown:")
    for s, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {s}: {n}")
    print(f"\nTotal OCDS paths mapped: {len(MAPPINGS)}")
    print(f"Vocabulary translations: {len(VOCAB)}")
    print(f"NZ extensions proposed: {len(EXTENSIONS)}")
    print(f"Rules cross-referenced: {len(RULES)}")
    print(f"Templates inventoried: {len(TEMPLATES)}")


if __name__ == "__main__":
    main()
