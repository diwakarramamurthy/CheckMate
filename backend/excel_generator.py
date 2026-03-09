"""
RERA Reports Excel Generator - Goa State Official Format
Generates Excel (.xlsx) versions of Form-1, Form-3, Form-4, and Annexure-A
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
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


# ─── Shared Styles ───────────────────────────────────────────────────────────

TITLE_FILL    = PatternFill(start_color="1F3864", end_color="1F3864", fill_type="solid")
HEADER_FILL   = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
SECTION_FILL  = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
TOTAL_FILL    = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

THIN = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def title_cell(cell, text):
    cell.value = text
    cell.font = Font(bold=True, size=13, color="FFFFFF")
    cell.fill = TITLE_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def header_cell(cell, text):
    cell.value = text
    cell.font = Font(bold=True, size=9, color="FFFFFF")
    cell.fill = HEADER_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = THIN


def section_cell(cell, text):
    cell.value = text
    cell.font = Font(bold=True, size=10)
    cell.fill = SECTION_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = THIN


def total_cell(cell, text, align="right"):
    cell.value = text
    cell.font = Font(bold=True, size=9)
    cell.fill = TOTAL_FILL
    cell.alignment = Alignment(horizontal=align, vertical="center")
    cell.border = THIN


def data_cell(cell, text, align="left", bold=False):
    cell.value = text
    cell.font = Font(size=9, bold=bold)
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
    cell.border = THIN


def label_cell(cell, text):
    cell.value = text
    cell.font = Font(bold=True, size=10)
    cell.alignment = Alignment(horizontal="left", vertical="center")


def value_cell(cell, text):
    cell.value = str(text) if text else ""
    cell.font = Font(size=10)
    cell.alignment = Alignment(horizontal="left", vertical="center")


# ─── FORM 1 ──────────────────────────────────────────────────────────────────

def generate_form1_excel(project, buildings, construction_progress, infrastructure_progress, quarter, year):
    wb = Workbook()

    # ── Sheet 1: Project Info ─────────────────────────────────────────────
    ws = wb.active
    ws.title = "Project Info"

    ws.merge_cells("A1:F1")
    title_cell(ws["A1"], "The Goa Real Estate (Regulation and Development) Rules 2017")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:F2")
    title_cell(ws["A2"], "FORM 1 — ARCHITECT'S CERTIFICATE")
    ws.row_dimensions[2].height = 24

    ws.merge_cells("A3:F3")
    ws["A3"].value = "(Percentage of Completion of Construction)"
    ws["A3"].font = Font(italic=True, size=10, color="FFFFFF")
    ws["A3"].fill = TITLE_FILL
    ws["A3"].alignment = Alignment(horizontal="center")

    info_rows = [
        ("Project Name:", project.get("project_name", "")),
        ("RERA Registration No.:", project.get("rera_number", "")),
        ("Report Period:", f"{quarter} {year}"),
        ("Report Date:", datetime.now().strftime("%d/%m/%Y")),
        ("Promoter Name:", project.get("promoter_name", "")),
        ("Architect Name:", project.get("architect_name", "")),
        ("Architect License No.:", project.get("architect_license", "")),
        ("Village / Panchayat:", project.get("village", "")),
        ("Taluka:", project.get("taluka", "")),
        ("District:", project.get("district", "North Goa")),
        ("Survey No. / Plot No.:", project.get("survey_number", "")),
        ("Total Area (sq.m.):", str(project.get("total_area", ""))),
    ]
    for i, (lbl, val) in enumerate(info_rows, 5):
        ws.merge_cells(f"A{i}:B{i}")
        label_cell(ws[f"A{i}"], lbl)
        ws.merge_cells(f"C{i}:F{i}")
        value_cell(ws[f"C{i}"], val)

    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 22
    for col in ["C", "D", "E", "F"]:
        ws.column_dimensions[col].width = 18

    # ── Sheet 2: Table A — Building Progress ──────────────────────────────
    progress_lookup = {p.get("building_id"): p for p in (construction_progress or [])}

    ws_a = wb.create_sheet("Table A - Buildings")
    ws_a.merge_cells("A1:E1")
    title_cell(ws_a["A1"], "TABLE A: Percentage of Completion per Building/Wing")
    ws_a.row_dimensions[1].height = 28

    ws_a.merge_cells("A2:E2")
    ws_a["A2"].value = (
        f"Project: {project.get('project_name', '')}  |  "
        f"RERA No: {project.get('rera_number', '')}  |  Period: {quarter} {year}"
    )
    ws_a["A2"].font = Font(size=10)
    ws_a.row_dimensions[2].height = 18

    for col, hdr in enumerate(["Sr. No.", "Building / Wing", "Activity", "% Work Done", "Remarks"], 1):
        header_cell(ws_a.cell(row=4, column=col), hdr)
    ws_a.row_dimensions[4].height = 28

    row = 5
    sr = 1
    for building in (buildings or []):
        bname = building.get("building_name", "Building")
        progress = progress_lookup.get(building.get("building_id"), {})
        ta = progress.get("tower_activities", {})

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

        # Building header
        ws_a.merge_cells(f"A{row}:E{row}")
        section_cell(
            ws_a[f"A{row}"],
            f"Building: {bname}  —  Overall Completion: {progress.get('overall_completion', 0):.1f}%",
        )
        ws_a.row_dimensions[row].height = 20
        row += 1

        activities = [
            ("Excavation",
             f"{plinth.get('excavation', {}).get('completion', 0):.0f}%"),
            ("Basements and Plinth",
             f"{get_cat_avg(plinth):.0f}%"),
            (f"{building.get('residential_floors', 0)} Slabs of Super Structure",
             f"{get_cat_avg(slab):.0f}%"),
            ("Internal Walls, Plaster, Flooring (Brickwork & Plastering)",
             f"{get_cat_avg(brickwk):.0f}%"),
            ("Doors and Windows",
             f"{(get_cat_avg(doors) + get_cat_avg(windows)) / 2:.0f}%"),
            ("Sanitary and Electrical Fittings",
             f"{(get_cat_avg(plumbing) + get_cat_avg(elec)) / 2:.0f}%"),
            ("Tiling / Flooring",
             f"{get_cat_avg(tiling):.0f}%"),
            ("Water Proofing",
             f"{get_cat_avg(waterp):.0f}%"),
            ("Painting",
             f"{get_cat_avg(painting):.0f}%"),
            ("Carpark",
             f"{get_cat_avg(carpark):.0f}%"),
        ]
        for act_name, pct in activities:
            data_cell(ws_a.cell(row=row, column=1), str(sr), align="center")
            ws_a.merge_cells(f"B{row}:C{row}")
            data_cell(ws_a.cell(row=row, column=2), act_name)
            ws_a.cell(row=row, column=3).border = THIN
            data_cell(ws_a.cell(row=row, column=4), pct, align="center")
            ws_a.cell(row=row, column=5).border = THIN
            sr += 1
            row += 1
        row += 1  # blank spacer

    ws_a.column_dimensions["A"].width = 8
    ws_a.column_dimensions["B"].width = 35
    ws_a.column_dimensions["C"].width = 12
    ws_a.column_dimensions["D"].width = 15
    ws_a.column_dimensions["E"].width = 22

    # ── Sheet 3: Table B — Infrastructure ─────────────────────────────────
    ws_b = wb.create_sheet("Table B - Infrastructure")
    ws_b.merge_cells("A1:F1")
    title_cell(ws_b["A1"], "TABLE B: Internal & External Development Works")
    ws_b.row_dimensions[1].height = 28

    for col, hdr in enumerate(
        ["Sr. No.", "Common Areas / Facilities", "Proposed (Yes/No)", "% Work Done", "Details"], 1
    ):
        header_cell(ws_b.cell(row=3, column=col), hdr)
    ws_b.row_dimensions[3].height = 28

    infra = infrastructure_progress.get("activities", {}) if infrastructure_progress else {}

    def ic(key):
        return infra.get(key, {}).get("completion", 0)

    infra_rows = [
        ("1.", "Internal Roads & Footpaths", "Yes", f"{ic('road_footpath_storm_drain'):.0f}%"),
        ("2.", "Water Supply", "Yes", f"{ic('underground_water_distribution'):.0f}%"),
        ("3.", "Sewerage (STP)", "Yes", f"{ic('underground_sewage_network'):.0f}%"),
        ("4.", "Storm Water Drains", "Yes", f"{ic('road_footpath_storm_drain'):.0f}%"),
        ("5.", "Landscaping & Tree Planting", "Yes", f"{ic('gardens_playground'):.0f}%"),
        ("6.", "Street Lighting", "Yes", f"{ic('street_lights'):.0f}%"),
        ("7.", "Community Buildings (Club House)", "Yes", f"{ic('club_house'):.0f}%"),
        ("8.", "Treatment & Disposal of Sewage", "Yes", f"{ic('sewage_treatment_plant'):.0f}%"),
        ("9.", "Solid Waste Management", "Yes", "0%"),
        ("10.", "Water Conservation / Rain Water Harvesting", "Yes", f"{ic('overhead_sump_reservoir'):.0f}%"),
        ("11.", "Energy Management", "Yes", f"{ic('electric_substation_cables'):.0f}%"),
        ("12.", "Fire Protection & Safety", "Yes", "0%"),
        ("13.", "Electrical Meter Room / Substation", "Yes", f"{ic('electric_substation_cables'):.0f}%"),
        ("14.", "Swimming Pool", "Yes", f"{ic('swimming_pool'):.0f}%"),
        ("15.", "Amphitheatre", "Yes", f"{ic('amphitheatre'):.0f}%"),
        ("16.", "Boundary Wall & Entry Gate", "Yes",
         f"{(ic('boundary_wall') + ic('entry_gate')) / 2:.0f}%"),
    ]
    for r, (sr_no, item, proposed, pct) in enumerate(infra_rows, 4):
        data_cell(ws_b.cell(row=r, column=1), sr_no, align="center")
        data_cell(ws_b.cell(row=r, column=2), item)
        data_cell(ws_b.cell(row=r, column=3), proposed, align="center")
        data_cell(ws_b.cell(row=r, column=4), pct, align="center")
        ws_b.cell(row=r, column=5).border = THIN

    ws_b.column_dimensions["A"].width = 8
    ws_b.column_dimensions["B"].width = 42
    ws_b.column_dimensions["C"].width = 16
    ws_b.column_dimensions["D"].width = 14
    ws_b.column_dimensions["E"].width = 22

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ─── FORM 3 ──────────────────────────────────────────────────────────────────

def generate_form3_excel(project, buildings, building_costs, estimated_dev_cost, quarter, year):
    wb = Workbook()
    ws = wb.active
    ws.title = "Form 3 - Cost Incurred"

    ws.merge_cells("A1:F1")
    title_cell(ws["A1"], "The Goa Real Estate (Regulation and Development) Rules 2017")
    ws.row_dimensions[1].height = 28
    ws.merge_cells("A2:F2")
    title_cell(ws["A2"], "FORM 3 — ENGINEER'S CERTIFICATE")
    ws.row_dimensions[2].height = 24
    ws.merge_cells("A3:F3")
    ws["A3"].value = "(Cost Incurred Statement for Development)"
    ws["A3"].font = Font(italic=True, size=10, color="FFFFFF")
    ws["A3"].fill = TITLE_FILL
    ws["A3"].alignment = Alignment(horizontal="center")

    info = [
        ("Project Name:", project.get("project_name", "")),
        ("RERA No.:", project.get("rera_number", "")),
        ("Report Period:", f"{quarter} {year}"),
        ("Report Date:", datetime.now().strftime("%d/%m/%Y")),
        ("Engineer Name:", project.get("engineer_name", "")),
        ("Engineer License No.:", project.get("engineer_license", "")),
    ]
    for i, (lbl, val) in enumerate(info, 5):
        ws.merge_cells(f"A{i}:B{i}")
        label_cell(ws[f"A{i}"], lbl)
        ws.merge_cells(f"C{i}:F{i}")
        value_cell(ws[f"C{i}"], val)

    # TABLE A
    row = 12
    ws.merge_cells(f"A{row}:F{row}")
    section_cell(ws[f"A{row}"], "TABLE A: Cost Incurred for Building Construction")
    ws.row_dimensions[row].height = 22
    row += 1

    hdrs = ["Sr.", "Building / Wing", "Estimated Cost (₹)", "Cost Incurred (₹)", "Balance (₹)", "% Utilized"]
    for c, h in enumerate(hdrs, 1):
        header_cell(ws.cell(row=row, column=c), h)
    ws.row_dimensions[row].height = 28
    row += 1

    bc_lookup = {bc.get("building_id"): bc for bc in (building_costs or [])}
    total_est = total_inc = 0

    for idx, b in enumerate(buildings or [], 1):
        bc = bc_lookup.get(b.get("building_id"), {})
        est = b.get("estimated_cost", 0)
        inc = bc.get("actual_cost", 0)
        bal = est - inc
        pct_used = f"{(inc / est * 100):.1f}%" if est > 0 else "0%"
        total_est += est
        total_inc += inc

        data_cell(ws.cell(row=row, column=1), str(idx), align="center")
        data_cell(ws.cell(row=row, column=2), b.get("building_name", ""))
        data_cell(ws.cell(row=row, column=3), format_indian_number(est), align="right")
        data_cell(ws.cell(row=row, column=4), format_indian_number(inc), align="right")
        data_cell(ws.cell(row=row, column=5), format_indian_number(bal), align="right")
        data_cell(ws.cell(row=row, column=6), pct_used, align="center")
        row += 1

    for c in range(1, 7):
        total_cell(ws.cell(row=row, column=c), "")
    total_cell(ws.cell(row=row, column=2), "TOTAL", align="center")
    total_cell(ws.cell(row=row, column=3), format_indian_number(total_est))
    total_cell(ws.cell(row=row, column=4), format_indian_number(total_inc))
    total_cell(ws.cell(row=row, column=5), format_indian_number(total_est - total_inc))
    row += 2

    # TABLE B — Infrastructure placeholder
    ws.merge_cells(f"A{row}:F{row}")
    section_cell(ws[f"A{row}"], "TABLE B: Cost of Internal/External Development Works")
    ws.row_dimensions[row].height = 22
    row += 1

    est_c = estimated_dev_cost or {}
    infra_cost = est_c.get("infrastructure_cost", 0)
    b_hdrs = ["Sr.", "Development Work", "Estimated (₹)", "Incurred (₹)", "Balance (₹)", ""]
    for c, h in enumerate(b_hdrs, 1):
        header_cell(ws.cell(row=row, column=c), h)
    ws.row_dimensions[row].height = 28
    row += 1

    b_rows = [
        ("1", "Internal Roads & Footpaths"), ("2", "Water Supply & Distribution"),
        ("3", "Sewerage & STP"), ("4", "Storm Water Drains"),
        ("5", "Landscaping"), ("6", "Street Lighting"),
        ("7", "Club House"), ("8", "Swimming Pool"),
        ("9", "Electrical Infrastructure"), ("10", "Boundary Wall & Gate"),
    ]
    for sr_no, work in b_rows:
        data_cell(ws.cell(row=row, column=1), sr_no, align="center")
        data_cell(ws.cell(row=row, column=2), work)
        for c in range(3, 7):
            data_cell(ws.cell(row=row, column=c), "—", align="center")
        row += 1

    for c in range(1, 7):
        total_cell(ws.cell(row=row, column=c), "")
    total_cell(ws.cell(row=row, column=2), "TOTAL INFRASTRUCTURE", align="center")
    total_cell(ws.cell(row=row, column=3), format_indian_number(infra_cost))
    total_cell(ws.cell(row=row, column=4), "—", align="center")
    total_cell(ws.cell(row=row, column=5), "—", align="center")

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 28
    for col in ["C", "D", "E"]:
        ws.column_dimensions[col].width = 20
    ws.column_dimensions["F"].width = 14

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ─── FORM 4 ──────────────────────────────────────────────────────────────────

def generate_form4_excel(project, project_cost, estimated_dev_cost, quarter, year):
    wb = Workbook()
    ws = wb.active
    ws.title = "Form 4 - Project Cost"

    ws.merge_cells("A1:E1")
    title_cell(ws["A1"], "The Goa Real Estate (Regulation and Development) Rules 2017")
    ws.row_dimensions[1].height = 28
    ws.merge_cells("A2:E2")
    title_cell(ws["A2"], "FORM 4 — CHARTERED ACCOUNTANT'S CERTIFICATE")
    ws.row_dimensions[2].height = 24
    ws.merge_cells("A3:E3")
    ws["A3"].value = "(Project Cost Statement)"
    ws["A3"].font = Font(italic=True, size=10, color="FFFFFF")
    ws["A3"].fill = TITLE_FILL
    ws["A3"].alignment = Alignment(horizontal="center")

    info = [
        ("Project Name:", project.get("project_name", "")),
        ("RERA No.:", project.get("rera_number", "")),
        ("Report Period:", f"{quarter} {year}"),
        ("Report Date:", datetime.now().strftime("%d/%m/%Y")),
        ("CA Name:", project.get("ca_name", "")),
        ("Membership No.:", project.get("ca_membership", "")),
        ("Firm Registration No.:", project.get("ca_firm_reg", "")),
    ]
    for i, (lbl, val) in enumerate(info, 5):
        ws.merge_cells(f"A{i}:B{i}")
        label_cell(ws[f"A{i}"], lbl)
        ws.merge_cells(f"C{i}:E{i}")
        value_cell(ws[f"C{i}"], val)

    row = 13
    ws.merge_cells(f"A{row}:E{row}")
    section_cell(ws[f"A{row}"], "PROJECT COST STATEMENT")
    ws.row_dimensions[row].height = 22
    row += 1

    for c, h in enumerate(["Sr.", "Particulars", "Estimated Cost (₹)", "Actual Cost (₹)", "Variance (₹)"], 1):
        header_cell(ws.cell(row=row, column=c), h)
    ws.row_dimensions[row].height = 28
    row += 1

    est_c = estimated_dev_cost or {}
    land_cost     = est_c.get("land_cost", 0)
    building_cost = est_c.get("total_building_cost", 0)
    infra_cost    = est_c.get("infrastructure_cost", 0)
    other_cost    = est_c.get("other_costs", 0)
    total_est     = land_cost + building_cost + infra_cost + other_cost

    for sr_no, desc, est in [
        (1, "Cost of Land", land_cost),
        (2, "Cost of Construction of Buildings", building_cost),
        (3, "Cost of Development Works (Infrastructure)", infra_cost),
        (4, "Administrative & Other Costs", other_cost),
    ]:
        data_cell(ws.cell(row=row, column=1), str(sr_no), align="center")
        data_cell(ws.cell(row=row, column=2), desc)
        data_cell(ws.cell(row=row, column=3), format_indian_number(est), align="right")
        data_cell(ws.cell(row=row, column=4), "—", align="center")
        data_cell(ws.cell(row=row, column=5), "—", align="center")
        row += 1

    for c in range(1, 6):
        total_cell(ws.cell(row=row, column=c), "")
    total_cell(ws.cell(row=row, column=2), "TOTAL PROJECT COST", align="center")
    total_cell(ws.cell(row=row, column=3), format_indian_number(total_est))
    total_cell(ws.cell(row=row, column=4), "—", align="center")
    total_cell(ws.cell(row=row, column=5), "—", align="center")
    row += 2

    # Bank Details
    ws.merge_cells(f"A{row}:E{row}")
    section_cell(ws[f"A{row}"], "DESIGNATED BANK ACCOUNT DETAILS")
    ws.row_dimensions[row].height = 22
    row += 1

    for lbl, val in [
        ("Bank Name:", project.get("bank_name", "—")),
        ("Account Number:", project.get("bank_account_number", "—")),
        ("IFSC Code:", project.get("bank_ifsc", "—")),
        ("Branch:", project.get("bank_branch", "—")),
    ]:
        ws.merge_cells(f"A{row}:B{row}")
        label_cell(ws[f"A{row}"], lbl)
        ws.merge_cells(f"C{row}:E{row}")
        value_cell(ws[f"C{row}"], val or "—")
        row += 1

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 38
    for col in ["C", "D", "E"]:
        ws.column_dimensions[col].width = 22

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


# ─── ANNEXURE-A ──────────────────────────────────────────────────────────────

def generate_annexure_a_excel(project, sales, buildings, quarter, year):
    wb = Workbook()
    ws = wb.active
    ws.title = "Annexure A - Receivables"

    ws.merge_cells("A1:J1")
    title_cell(ws["A1"], "ANNEXURE - A: Statement of Receivables from Allottees")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:J2")
    ws["A2"].value = (
        f"Project: {project.get('project_name', '')}  |  "
        f"RERA No: {project.get('rera_number', '')}  |  "
        f"Period: {quarter} {year}  |  Date: {datetime.now().strftime('%d/%m/%Y')}"
    )
    ws["A2"].font = Font(size=10)
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 18

    headers = [
        "Sr.", "Unit No.", "Building / Wing", "Type", "Area (sq.m.)",
        "Agreement Value (₹)", "Amount Received (₹)", "Balance Due (₹)",
        "Due Date", "Allottee Name",
    ]
    for c, h in enumerate(headers, 1):
        header_cell(ws.cell(row=4, column=c), h)
    ws.row_dimensions[4].height = 35

    bl = {b.get("building_id"): b.get("building_name", "") for b in (buildings or [])}

    total_val = total_recv = total_bal = 0

    for idx, sale in enumerate(sales or [], 1):
        r = idx + 4
        agr = sale.get("agreement_value", 0)
        recv = sale.get("amount_received", 0)
        bal = agr - recv
        total_val  += agr
        total_recv += recv
        total_bal  += bal

        data_cell(ws.cell(row=r, column=1),  str(idx), align="center")
        data_cell(ws.cell(row=r, column=2),  sale.get("unit_number", ""), align="center")
        data_cell(ws.cell(row=r, column=3),  bl.get(sale.get("building_id"), ""))
        data_cell(ws.cell(row=r, column=4),  sale.get("unit_type", ""), align="center")
        data_cell(ws.cell(row=r, column=5),  str(sale.get("carpet_area", "")), align="center")
        data_cell(ws.cell(row=r, column=6),  format_indian_number(agr), align="right")
        data_cell(ws.cell(row=r, column=7),  format_indian_number(recv), align="right")
        data_cell(ws.cell(row=r, column=8),  format_indian_number(bal), align="right")
        data_cell(ws.cell(row=r, column=9),  sale.get("due_date", ""), align="center")
        data_cell(ws.cell(row=r, column=10), sale.get("allottee_name", ""))

    total_row = len(sales or []) + 5
    for c in range(1, 11):
        total_cell(ws.cell(row=total_row, column=c), "")
    total_cell(ws.cell(row=total_row, column=5),  "TOTAL",                          align="center")
    total_cell(ws.cell(row=total_row, column=6),  format_indian_number(total_val))
    total_cell(ws.cell(row=total_row, column=7),  format_indian_number(total_recv))
    total_cell(ws.cell(row=total_row, column=8),  format_indian_number(total_bal))

    # Summary
    sr = total_row + 2
    ws.merge_cells(f"A{sr}:J{sr}")
    ws[f"A{sr}"].value = (
        f"Summary: Total Units: {len(sales or [])}  |  "
        f"Total Agreement Value: ₹{format_indian_number(total_val)}  |  "
        f"Total Received: ₹{format_indian_number(total_recv)}  |  "
        f"Total Balance Due: ₹{format_indian_number(total_bal)}"
    )
    ws[f"A{sr}"].font = Font(bold=True, size=10)
    ws[f"A{sr}"].fill = SECTION_FILL
    ws[f"A{sr}"].alignment = Alignment(horizontal="left", vertical="center")

    col_widths = [6, 10, 16, 12, 12, 22, 22, 20, 14, 26]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
