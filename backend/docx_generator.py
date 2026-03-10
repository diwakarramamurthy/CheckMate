"""
RERA Reports Word Document Generator - Goa State Official Format
Generates Word (.docx) versions of Form-1, Form-3, Form-4, and Annexure-A
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
from datetime import datetime


# ─── Helpers ────────────────────────────────────────────────────────────────

def format_indian_number(num):
    if num is None or num == 0:
        return "0"
    num = int(num)
    is_negative = num < 0
    num = abs(num)
    s = str(num)
    if len(s) <= 3:
        result = s
    else:
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
    return ("-" + result) if is_negative else result


def get_cat_avg(cat_data):
    if not cat_data:
        return 0
    vals = [v.get("completion", 0) for v in cat_data.values() if isinstance(v, dict)]
    return sum(vals) / len(vals) if vals else 0


# ─── Cell Styling Helpers ─────────────────────────────────────────────────────

def shade_cell(cell, hex_color):
    """Set background colour for a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def border_cell(cell, color="000000", size="4"):
    """Add thin borders to all sides of a cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "bottom", "left", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), size)
        b.set(qn("w:color"), color)
        tcBorders.append(b)
    tcPr.append(tcBorders)


def set_col_width(table, col_index, width_cm):
    """Set width of a specific column in a table."""
    from docx.oxml.ns import qn as _qn
    from docx.oxml import OxmlElement as _OE
    from docx.shared import Cm as _Cm
    for row in table.rows:
        cell = row.cells[col_index]
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcW = _OE("w:tcW")
        tcW.set(_qn("w:w"), str(int(_Cm(width_cm).emu / 914.4 * 20)))
        tcW.set(_qn("w:type"), "dxa")
        tcPr.append(tcW)


# ─── Paragraph / Run Helpers ──────────────────────────────────────────────────

def add_para(doc, text="", size=10, bold=False, italic=False,
             align=WD_ALIGN_PARAGRAPH.LEFT, color=None, space_after=Pt(4)):
    para = doc.add_paragraph()
    para.alignment = align
    para.paragraph_format.space_after = space_after
    run = para.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    return para


def add_title_block(doc, form_num, title_text, subtitle_text):
    for line in [
        "The Goa Real Estate (Regulation and Development)",
        "(Registration of Real Estate Projects, Registration of Real Estate Agents,",
        "Rates of Interest and Disclosures on Website) Rules 2017",
    ]:
        p = add_para(doc, line, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_para(doc, "")
    add_para(doc, form_num, size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "(See Rule 5 (1) (a) (ii))", size=9, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, title_text, size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, subtitle_text, size=9, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "")


def add_info_table(doc, rows):
    """Rows: list of (label, value) tuples."""
    t = doc.add_table(rows=len(rows), cols=2)
    t.style = "Table Grid"
    for i, (lbl, val) in enumerate(rows):
        c0, c1 = t.cell(i, 0), t.cell(i, 1)
        c0.text = lbl
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(10)
        c1.text = str(val) if val else ""
        c1.paragraphs[0].runs[0].font.size = Pt(10)
        shade_cell(c0, "D9E1F2")
    return t


def add_section_heading(doc, text, color=(0x1F, 0x38, 0x64)):
    p = add_para(doc, text, size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=color)
    return p


def add_data_table(doc, rows, header_bg="4472C4", total_bg="E2EFDA"):
    """rows[0] = header. rows[-1] can be a total row (handled by caller)."""
    n_cols = len(rows[0])
    t = doc.add_table(rows=len(rows), cols=n_cols)
    t.style = "Table Grid"

    for r_idx, row_data in enumerate(rows):
        is_header = r_idx == 0
        is_total  = r_idx == len(rows) - 1 and len(rows) > 2

        for c_idx, val in enumerate(row_data):
            cell = t.cell(r_idx, c_idx)
            cell.text = str(val) if val is not None else ""
            para = cell.paragraphs[0]
            run  = para.runs[0] if para.runs else para.add_run(str(val) if val is not None else "")
            run.font.size = Pt(9)
            run.font.bold = is_header or is_total
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            border_cell(cell)

            if is_header:
                shade_cell(cell, header_bg)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            elif is_total:
                shade_cell(cell, total_bg)

    return t


def section_margins(doc):
    for section in doc.sections:
        section.top_margin    = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin   = Cm(2.0)
        section.right_margin  = Cm(2.0)


# ─── FORM 1 ──────────────────────────────────────────────────────────────────

def generate_form1_docx(project, buildings, construction_progress, infrastructure_progress, quarter, year):
    doc = Document()
    section_margins(doc)

    add_title_block(doc, "FORM 1", "ARCHITECT'S / LICENSED SURVEYOR'S CERTIFICATE",
                    "(To be submitted at the time of Registration and for withdrawal of Money from Designated Account)")

    # "To" block
    add_para(doc, "To", bold=True)
    for line in [
        project.get("promoter_name", "________________________"),
        project.get("promoter_address", project.get("address", "________________________")),
        f"{project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}",
    ]:
        add_para(doc, line, size=10)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_date.add_run(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    r.font.bold = True
    r.font.size = Pt(10)

    add_para(doc, "")

    # Project info table
    add_info_table(doc, [
        ("Project Name",            project.get("project_name", "")),
        ("RERA Registration No.",   project.get("rera_number", "")),
        ("Report Period",           f"{quarter} {year}"),
        ("Promoter Name",           project.get("promoter_name", "")),
        ("Architect Name",          project.get("architect_name", "")),
        ("Architect License No.",   project.get("architect_license", "")),
        ("Survey No. / Plot No.",   project.get("survey_number", "")),
        ("Total Area (sq.m.)",      str(project.get("total_area", ""))),
        ("Village / Taluka",        f"{project.get('village', '')}, {project.get('taluka', '')}"),
        ("District",                project.get("district", "North Goa")),
    ])

    add_para(doc, "")

    # Assignment text
    num_buildings = len(buildings) if buildings else "__"
    phase = project.get("phase", "1")
    add_para(doc, (
        f"I/We {project.get('architect_name', '________________________')} have undertaken assignment as "
        f"Architect / Licensed Surveyor of certifying Percentage of Completion of Construction Work of "
        f"{num_buildings} Building(s) / Wing(s) of the {phase} Phase of the Project, "
        f"RERA No. {project.get('rera_number', '________')}."
    ), size=10)

    # TABLE A for each building
    progress_lookup = {p.get("building_id"): p for p in (construction_progress or [])}

    for building in (buildings or []):
        bname    = building.get("building_name", "Building")
        progress = progress_lookup.get(building.get("building_id"), {})
        ta       = progress.get("tower_activities", {})

        plinth   = ta.get("plinth_completion", {})
        slab     = ta.get("slab_completion", {})
        brickwk  = ta.get("brickwork_plastering", {})
        plumbing = ta.get("plumbing", {})
        elec     = ta.get("electrical_works", {})
        windows  = ta.get("window_works", {})
        tiling   = ta.get("tiling_flooring", {})
        doors    = ta.get("door_shutter_fixing", {})
        waterp   = ta.get("water_proofing", {})
        painting = ta.get("painting", {})
        carpark  = ta.get("carpark", {})

        add_para(doc, "")
        add_section_heading(
            doc,
            f"TABLE A: Building / Wing — {bname}  (Overall Completion: {progress.get('overall_completion', 0):.1f}%)"
        )

        rows_a = [
            ["Sr. No.", "Tasks / Activity", "Percentage of Work Done"],
            ["1",  "Excavation",
             f"{plinth.get('excavation', {}).get('completion', 0):.0f}%"],
            ["2",  f"{building.get('basements', 0)} Basement(s) and Plinth",
             f"{get_cat_avg(plinth):.0f}%"],
            ["3",  f"{building.get('residential_floors', 0)} Slabs of Super Structure",
             f"{get_cat_avg(slab):.0f}%"],
            ["4",  "Internal Walls, Internal Plaster, Flooring",
             f"{get_cat_avg(brickwk):.0f}%"],
            ["5",  "Doors and Windows",
             f"{(get_cat_avg(doors) + get_cat_avg(windows)) / 2:.0f}%"],
            ["6",  "Sanitary and Electrical Fittings",
             f"{(get_cat_avg(plumbing) + get_cat_avg(elec)) / 2:.0f}%"],
            ["7",  "Tiling / Flooring",
             f"{get_cat_avg(tiling):.0f}%"],
            ["8",  "External Plumbing / Plaster, Elevation, Terrace Waterproofing, Painting",
             f"{(get_cat_avg(waterp) + get_cat_avg(painting)) / 2:.0f}%"],
            ["9",  "Carpark",
             f"{get_cat_avg(carpark):.0f}%"],
        ]
        add_data_table(doc, rows_a)

        doc.add_page_break()

    # TABLE B — Infrastructure
    add_section_heading(doc, "TABLE B: Internal & External Development Works in Respect of the Registered Phase")
    add_para(doc, "")

    infra = infrastructure_progress.get("activities", {}) if infrastructure_progress else {}

    def ic(key):
        return infra.get(key, {}).get("completion", 0)

    rows_b = [
        ["Sr. No.", "Common Areas and Facilities / Amenities", "Proposed\n(Yes/No)", "% Work Done", "Details"],
        ["1.",  "Internal Roads & Footpaths",               "Yes", f"{ic('road_footpath_storm_drain'):.0f}%",       ""],
        ["2.",  "Water Supply",                              "Yes", f"{ic('underground_water_distribution'):.0f}%",  ""],
        ["3.",  "Sewerage (STP)",                            "Yes", f"{ic('underground_sewage_network'):.0f}%",      ""],
        ["4.",  "Storm Water Drains",                        "Yes", f"{ic('road_footpath_storm_drain'):.0f}%",       ""],
        ["5.",  "Landscaping & Tree Planting",               "Yes", f"{ic('gardens_playground'):.0f}%",             ""],
        ["6.",  "Street Lighting",                           "Yes", f"{ic('street_lights'):.0f}%",                  ""],
        ["7.",  "Community Buildings (Club House)",          "Yes", f"{ic('club_house'):.0f}%",                     ""],
        ["8.",  "Treatment & Disposal of Sewage",            "Yes", f"{ic('sewage_treatment_plant'):.0f}%",         ""],
        ["9.",  "Solid Waste Management",                    "Yes", "0%",                                            ""],
        ["10.", "Rain Water Harvesting",                     "Yes", f"{ic('overhead_sump_reservoir'):.0f}%",        ""],
        ["11.", "Energy Management",                         "Yes", f"{ic('electric_substation_cables'):.0f}%",     ""],
        ["12.", "Fire Protection & Safety",                  "Yes", "0%",                                            ""],
        ["13.", "Electrical Meter Room / Substation",        "Yes", f"{ic('electric_substation_cables'):.0f}%",     ""],
        ["14.", "Swimming Pool",                             "Yes", f"{ic('swimming_pool'):.0f}%",                  ""],
        ["15.", "Amphitheatre",                              "Yes", f"{ic('amphitheatre'):.0f}%",                   ""],
        ["16.", "Boundary Wall & Entry Gate",                "Yes",
         f"{(ic('boundary_wall') + ic('entry_gate')) / 2:.0f}%",                                                    ""],
    ]
    add_data_table(doc, rows_b)

    add_para(doc, "")
    add_para(doc, "Yours Faithfully,", bold=True)
    add_para(doc, "")
    add_para(doc, "")
    add_para(doc, "_______________________________")
    add_para(doc, f"Signature & Name: {project.get('architect_name', '________________________')}", bold=True)
    add_para(doc, f"License No.: {project.get('architect_license', '________________________')}")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# ─── FORM 3 ──────────────────────────────────────────────────────────────────

def generate_form3_docx(project, buildings, construction_progress, infrastructure_progress, estimated_dev_cost, quarter, year):
    """Form-3: Cost Incurred = (% Work Completed from Construction Progress) × Estimated Cost"""
    doc = Document()
    section_margins(doc)

    add_title_block(doc, "FORM 3", "ENGINEER'S CERTIFICATE", "(Cost Incurred Statement for Development)")

    add_para(doc, "To", bold=True)
    for line in [
        project.get("promoter_name", "________________________"),
        project.get("promoter_address", project.get("address", "________________________")),
        f"{project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}",
    ]:
        add_para(doc, line, size=10)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_date.add_run(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    r.font.bold = True
    r.font.size = Pt(10)

    add_para(doc, "")
    add_info_table(doc, [
        ("Project Name",            project.get("project_name", "")),
        ("RERA No.",                project.get("rera_number", "")),
        ("Report Period",           f"{quarter} {year}"),
        ("Report Date",             datetime.now().strftime("%d/%m/%Y")),
        ("Engineer Name",           project.get("engineer_name", "")),
        ("Engineer License No.",    project.get("engineer_license", "")),
    ])

    add_para(doc, "")
    add_para(doc, (
        f"I/We {project.get('engineer_name', '________________________')}, Engineer, have examined the "
        f"project site and hereby certify the cost incurred for development of the project "
        f"{project.get('project_name', '________')}, RERA No. {project.get('rera_number', '________')}."
    ), size=10)

    # TABLE A — Cost Incurred = completion% × estimated_cost
    add_para(doc, "")
    add_section_heading(doc, "TABLE A: Cost Incurred for Building Construction")

    cp_lookup = {cp.get("building_id"): cp for cp in (construction_progress or [])}
    total_est = total_inc = 0

    rows_a = [["Sr.", "Building / Wing", "% Complete", "Estimated Cost (₹)", "Cost Incurred (₹)", "Balance (₹)"]]
    for idx, b in enumerate(buildings or [], 1):
        progress = cp_lookup.get(b.get("building_id"), {})
        completion_pct = progress.get("overall_completion", 0)
        est = b.get("estimated_cost", 0)
        inc = round((completion_pct / 100) * est)
        bal = est - inc
        total_est += est
        total_inc += inc
        rows_a.append([str(idx), b.get("building_name", ""),
                        f"{completion_pct:.1f}%",
                        format_indian_number(est), format_indian_number(inc), format_indian_number(bal)])
    rows_a.append(["", "TOTAL", "",
                   format_indian_number(total_est), format_indian_number(total_inc),
                   format_indian_number(total_est - total_inc)])

    add_data_table(doc, rows_a)

    # TABLE B — Infra Cost Incurred = completion% × estimated_infra_cost
    add_para(doc, "")
    add_section_heading(doc, "TABLE B: Cost of Internal / External Development Works")

    est_c = estimated_dev_cost or {}
    infra_cost = est_c.get("infrastructure_cost", 0)
    infra_completion = (infrastructure_progress or {}).get("overall_completion", 0)
    infra_incurred = round((infra_completion / 100) * infra_cost)
    infra_balance = infra_cost - infra_incurred

    rows_b = [
        ["Sr.", "Development Work", "Estimated (₹)", "Incurred (₹)", "Balance (₹)"],
        ["1", "Internal Roads & Footpaths", "—", "—", "—"],
        ["2", "Water Supply & Distribution", "—", "—", "—"],
        ["3", "Sewerage & STP", "—", "—", "—"],
        ["4", "Storm Water Drains", "—", "—", "—"],
        ["5", "Landscaping", "—", "—", "—"],
        ["6", "Street Lighting", "—", "—", "—"],
        ["7", "Club House", "—", "—", "—"],
        ["8", "Swimming Pool", "—", "—", "—"],
        ["9", "Electrical Infrastructure", "—", "—", "—"],
        ["10", "Boundary Wall & Gate", "—", "—", "—"],
        ["", "TOTAL INFRASTRUCTURE",
         format_indian_number(infra_cost),
         format_indian_number(infra_incurred),
         format_indian_number(infra_balance)],
    ]
    add_data_table(doc, rows_b)

    add_para(doc, "")
    add_para(doc, "Yours Faithfully,", bold=True)
    add_para(doc, "")
    add_para(doc, "")
    add_para(doc, "_______________________________")
    add_para(doc, f"Signature & Name: {project.get('engineer_name', '________________________')}", bold=True)
    add_para(doc, f"License No.: {project.get('engineer_license', '________________________')}")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# ─── FORM 4 ──────────────────────────────────────────────────────────────────

def generate_form4_docx(project, project_cost, estimated_dev_cost, quarter, year):
    doc = Document()
    section_margins(doc)

    add_title_block(doc, "FORM 4", "CHARTERED ACCOUNTANT'S CERTIFICATE", "(Project Cost Statement)")

    add_para(doc, "To", bold=True)
    for line in [
        project.get("promoter_name", "________________________"),
        project.get("promoter_address", project.get("address", "________________________")),
        f"{project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}",
    ]:
        add_para(doc, line, size=10)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_date.add_run(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    r.font.bold = True
    r.font.size = Pt(10)

    add_para(doc, "")
    add_info_table(doc, [
        ("Project Name",                project.get("project_name", "")),
        ("RERA No.",                    project.get("rera_number", "")),
        ("Report Period",               f"{quarter} {year}"),
        ("Report Date",                 datetime.now().strftime("%d/%m/%Y")),
        ("CA Name",                     project.get("ca_name", "")),
        ("CA Membership No.",           project.get("ca_membership", "")),
        ("CA Firm Registration No.",    project.get("ca_firm_reg", "")),
    ])

    add_para(doc, "")
    add_para(doc, (
        f"I/We {project.get('ca_name', '________________________')}, Chartered Accountant(s), have "
        f"examined the books of accounts and records of the promoter and certify the following with "
        f"respect to the project cost of {project.get('project_name', '________')}, "
        f"RERA No. {project.get('rera_number', '________')}."
    ), size=10)

    # Project Cost Table
    add_para(doc, "")
    add_section_heading(doc, "PROJECT COST STATEMENT")

    est_c = estimated_dev_cost or {}
    pc    = project_cost or {}

    # Estimated costs
    land_cost_est    = pc.get("total_land_cost_estimated", pc.get("land_acquisition_estimated", 0))
    building_cost_est = est_c.get("buildings_cost", est_c.get("total_building_cost", 0))
    infra_cost_est   = est_c.get("infrastructure_cost", 0)
    other_cost_est   = est_c.get("consultants_fee", 0) + est_c.get("machinery_cost", est_c.get("other_costs", 0))
    total_est        = land_cost_est + building_cost_est + infra_cost_est + other_cost_est

    # Actual costs from project_cost (CA-entered financial data)
    land_cost_act    = pc.get("total_land_cost", 0)
    building_cost_act = pc.get("construction_cost_actual", 0)
    infra_cost_act   = pc.get("onsite_services_cost", pc.get("infrastructure_cost", 0))
    other_cost_act   = pc.get("taxes_statutory", 0) + pc.get("finance_cost", 0)
    total_act        = pc.get("total_cost_incurred", land_cost_act + building_cost_act + infra_cost_act + other_cost_act)

    def fmt_act(v):
        return format_indian_number(v) if v else "—"

    cost_rows = [
        ["Sr.", "Particulars",                                        "Estimated Cost (₹)",               "Actual Cost (₹)"],
        ["1",   "Cost of Land",                                       format_indian_number(land_cost_est),    fmt_act(land_cost_act)],
        ["2",   "Cost of Construction of Buildings",                  format_indian_number(building_cost_est), fmt_act(building_cost_act)],
        ["3",   "Cost of Development Works (Infrastructure)",         format_indian_number(infra_cost_est),   fmt_act(infra_cost_act)],
        ["4",   "Administrative & Other Costs (Taxes, Finance)",      format_indian_number(other_cost_est),   fmt_act(other_cost_act)],
        ["",    "TOTAL PROJECT COST",                                 format_indian_number(total_est),        fmt_act(total_act)],
    ]
    add_data_table(doc, cost_rows)

    # Bank Details
    add_para(doc, "")
    add_section_heading(doc, "DESIGNATED BANK ACCOUNT DETAILS")
    add_info_table(doc, [
        ("Bank Name",       project.get("bank_name", "—")),
        ("Account Number",  project.get("bank_account_number", "—")),
        ("IFSC Code",       project.get("bank_ifsc", "—")),
        ("Branch",          project.get("designated_bank_name", "—")),
    ])

    add_para(doc, "")
    add_para(doc, "Yours Faithfully,", bold=True)
    add_para(doc, "")
    add_para(doc, "")
    add_para(doc, "_______________________________")
    add_para(doc, f"Signature & Name: {project.get('ca_name', '________________________')}", bold=True)
    add_para(doc, f"Membership No.: {project.get('ca_membership_number', '________________________')}")
    add_para(doc, f"Firm Registration No.: {project.get('ca_firm_name', '________________________')}")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# ─── ANNEXURE-A ──────────────────────────────────────────────────────────────

def generate_annexure_a_docx(project, sales, buildings, quarter, year):
    doc = Document()

    # Landscape layout
    for section in doc.sections:
        section.top_margin    = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin   = Cm(1.5)
        section.right_margin  = Cm(1.5)
        # Swap width/height for landscape
        w = section.page_width
        h = section.page_height
        section.page_width  = max(w, h)
        section.page_height = min(w, h)

    add_para(doc, "ANNEXURE - A", size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "Statement of Receivables from Allottees", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, (
        f"Project: {project.get('project_name', '')}  |  "
        f"RERA No: {project.get('rera_number', '')}  |  "
        f"Period: {quarter} {year}  |  Date: {datetime.now().strftime('%d/%m/%Y')}"
    ), size=10)
    add_para(doc, "")

    headers = [
        "Sr.", "Unit No.", "Building / Wing", "Type", "Area (sq.m.)",
        "Agreement Value (₹)", "Amount Received (₹)", "Balance Due (₹)",
        "Due Date", "Allottee Name",
    ]
    bl = {b.get("building_id"): b.get("building_name", "") for b in (buildings or [])}

    total_val = total_recv = total_bal = 0
    all_rows = [headers]

    for idx, sale in enumerate(sales or [], 1):
        agr  = sale.get("sale_value", sale.get("agreement_value", 0))
        recv = sale.get("amount_received", 0)
        bal  = agr - recv
        total_val  += agr
        total_recv += recv
        total_bal  += bal
        all_rows.append([
            str(idx),
            sale.get("unit_number", ""),
            bl.get(sale.get("building_id"), sale.get("building_name", "")),
            sale.get("unit_type", sale.get("flat_type", "")),
            str(sale.get("carpet_area", "")),
            format_indian_number(agr),
            format_indian_number(recv),
            format_indian_number(bal),
            sale.get("agreement_date", sale.get("due_date", "")),
            sale.get("buyer_name", sale.get("allottee_name", "")),
        ])

    if not sales:
        all_rows.append(["", "No sales data available"] + [""] * 8)

    all_rows.append([
        "", "", "", "", "TOTAL",
        format_indian_number(total_val),
        format_indian_number(total_recv),
        format_indian_number(total_bal),
        "", "",
    ])

    add_data_table(doc, all_rows)

    add_para(doc, "")
    add_para(doc, (
        f"Summary: Total Units: {len(sales or [])}  |  "
        f"Total Agreement Value: ₹{format_indian_number(total_val)}  |  "
        f"Total Received: ₹{format_indian_number(total_recv)}  |  "
        f"Total Balance Due: ₹{format_indian_number(total_bal)}"
    ), size=10, bold=True)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
