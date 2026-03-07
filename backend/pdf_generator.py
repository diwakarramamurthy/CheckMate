"""
RERA Forms PDF Generator - Goa State Format
Generates Form-1 to Form-6 and Annexure-A in official format
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4

# Styles
styles = getSampleStyleSheet()

# Custom styles
TITLE_STYLE = ParagraphStyle(
    'Title',
    parent=styles['Heading1'],
    fontSize=14,
    alignment=TA_CENTER,
    spaceAfter=12,
    fontName='Helvetica-Bold'
)

SUBTITLE_STYLE = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=11,
    alignment=TA_CENTER,
    spaceAfter=6,
    fontName='Helvetica-Bold'
)

HEADER_STYLE = ParagraphStyle(
    'Header',
    parent=styles['Normal'],
    fontSize=10,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

BODY_STYLE = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=9,
    alignment=TA_LEFT,
    fontName='Helvetica'
)

SMALL_STYLE = ParagraphStyle(
    'Small',
    parent=styles['Normal'],
    fontSize=8,
    alignment=TA_LEFT,
    fontName='Helvetica'
)

RIGHT_STYLE = ParagraphStyle(
    'Right',
    parent=styles['Normal'],
    fontSize=9,
    alignment=TA_RIGHT,
    fontName='Helvetica'
)

def format_currency(amount):
    """Format number as Indian currency"""
    if amount is None:
        return "0"
    return f"{amount:,.2f}"

def format_date(date_str):
    """Format date string"""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y")
    except:
        return date_str

def get_quarter_dates(quarter, year):
    """Get quarter date range"""
    quarters = {
        "Q1": ("01/01", "31/03"),
        "Q2": ("01/04", "30/06"),
        "Q3": ("01/07", "30/09"),
        "Q4": ("01/10", "31/12")
    }
    start, end = quarters.get(quarter, ("01/01", "31/03"))
    return f"{start}/{year}", f"{end}/{year}"


def generate_form1_pdf(project, buildings, construction_progress, infrastructure_progress, quarter, year):
    """
    FORM-1: Architect's Certificate - Percentage Completion of Construction
    Table A: Building-wise completion
    Table B: Common Development Works
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    start_date, end_date = get_quarter_dates(quarter, year)
    
    # Header
    elements.append(Paragraph("DEPARTMENT OF URBAN DEVELOPMENT", TITLE_STYLE))
    elements.append(Paragraph("GOVERNMENT OF GOA", SUBTITLE_STYLE))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>FORM - 1</b>", SUBTITLE_STYLE))
    elements.append(Paragraph("ARCHITECT'S / LICENSED SURVEYOR'S CERTIFICATE", SUBTITLE_STYLE))
    elements.append(Paragraph("(Percentage completion of Construction)", SMALL_STYLE))
    elements.append(Spacer(1, 12))
    
    # Project Details
    project_info = [
        ["Project Name:", project.get('project_name', ''), "RERA No:", project.get('rera_number', '')],
        ["Promoter:", project.get('promoter_name', ''), "Quarter:", f"{quarter} {year}"],
        ["Location:", f"{project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', '')}", "Report Date:", datetime.now().strftime("%d/%m/%Y")],
    ]
    
    project_table = Table(project_info, colWidths=[1.2*inch, 2.5*inch, 1*inch, 2*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(project_table)
    elements.append(Spacer(1, 20))
    
    # Table A: Building-wise Construction Progress
    elements.append(Paragraph("<b>TABLE A: Building-wise Percentage Completion of Construction</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    # Table A Headers
    table_a_headers = [
        "Sr.", "Building/\nWing", "Excavation", "Basement\n& Plinth", "Podiums", "Stilt\nFloor", 
        "Super\nStructure", "Internal\nWorks", "Doors/\nWindows", "Stairs/\nLifts", 
        "External\nFinish", "Final\nItems", "Overall\n%"
    ]
    
    table_a_data = [table_a_headers]
    
    # Build progress lookup
    progress_lookup = {p.get('building_id'): p for p in construction_progress}
    
    for idx, building in enumerate(buildings, 1):
        progress = progress_lookup.get(building.get('building_id'), {})
        tower_acts = progress.get('tower_activities', {})
        
        # Extract completion percentages from tower_activities
        plinth = tower_acts.get('plinth_completion', {})
        slab = tower_acts.get('slab_completion', {})
        brickwork = tower_acts.get('brickwork_plastering', {})
        plumbing = tower_acts.get('plumbing', {})
        electrical = tower_acts.get('electrical_works', {})
        windows = tower_acts.get('window_works', {})
        tiling = tower_acts.get('tiling_flooring', {})
        doors = tower_acts.get('door_shutter_fixing', {})
        waterproof = tower_acts.get('water_proofing', {})
        painting = tower_acts.get('painting', {})
        
        # Calculate category completions (simplified)
        def get_cat_avg(cat_data):
            if not cat_data:
                return 0
            total = sum(v.get('completion', 0) for v in cat_data.values() if isinstance(v, dict))
            count = sum(1 for v in cat_data.values() if isinstance(v, dict))
            return total / count if count > 0 else 0
        
        row = [
            str(idx),
            building.get('building_name', ''),
            f"{get_cat_avg(plinth):.0f}%",  # Excavation from plinth
            f"{get_cat_avg(plinth):.0f}%",  # Basement & Plinth
            "-",  # Podiums
            "-",  # Stilt
            f"{get_cat_avg(slab):.0f}%",  # Super Structure
            f"{get_cat_avg(brickwork):.0f}%",  # Internal Works
            f"{get_cat_avg(doors):.0f}%",  # Doors/Windows
            "-",  # Stairs/Lifts
            f"{get_cat_avg(waterproof):.0f}%",  # External Finish
            f"{get_cat_avg(painting):.0f}%",  # Final Items
            f"{progress.get('overall_completion', 0):.1f}%"
        ]
        table_a_data.append(row)
    
    # Create Table A
    col_widths = [0.35*inch, 0.6*inch] + [0.5*inch] * 11
    table_a = Table(table_a_data, colWidths=col_widths)
    table_a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table_a)
    elements.append(Spacer(1, 20))
    
    # Table B: Common Development Works
    elements.append(Paragraph("<b>TABLE B: Percentage Completion of Common Development Works</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    infra_data = infrastructure_progress.get('activities', {}) if infrastructure_progress else {}
    
    table_b_data = [
        ["Sr.", "Development Work", "Proposed", "% Completion"],
        ["1", "Road, Foot-path and storm water drain", "Yes", f"{infra_data.get('road_footpath_storm_drain', {}).get('completion', 0):.0f}%"],
        ["2", "Underground sewage drainage network", "Yes", f"{infra_data.get('underground_sewage_network', {}).get('completion', 0):.0f}%"],
        ["3", "Sewage Treatment Plant", "Yes", f"{infra_data.get('sewage_treatment_plant', {}).get('completion', 0):.0f}%"],
        ["4", "Over-head and Sump water reservoir/Tank", "Yes", f"{infra_data.get('overhead_sump_reservoir', {}).get('completion', 0):.0f}%"],
        ["5", "Under ground water distribution network", "Yes", f"{infra_data.get('underground_water_distribution', {}).get('completion', 0):.0f}%"],
        ["6", "Electric Substation & Under-ground cables", "Yes", f"{infra_data.get('electric_substation_cables', {}).get('completion', 0):.0f}%"],
        ["7", "Street Lights", "Yes", f"{infra_data.get('street_lights', {}).get('completion', 0):.0f}%"],
        ["8", "Entry Gate", "Yes", f"{infra_data.get('entry_gate', {}).get('completion', 0):.0f}%"],
        ["9", "Boundary wall", "Yes", f"{infra_data.get('boundary_wall', {}).get('completion', 0):.0f}%"],
        ["10", "Club House", "Yes", f"{infra_data.get('club_house', {}).get('completion', 0):.0f}%"],
        ["11", "Swimming Pool", "Yes", f"{infra_data.get('swimming_pool', {}).get('completion', 0):.0f}%"],
        ["12", "Amphitheatre", "Yes", f"{infra_data.get('amphitheatre', {}).get('completion', 0):.0f}%"],
        ["13", "Gardens / Play Ground", "Yes", f"{infra_data.get('gardens_playground', {}).get('completion', 0):.0f}%"],
    ]
    
    table_b = Table(table_b_data, colWidths=[0.5*inch, 4*inch, 0.8*inch, 1*inch])
    table_b.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table_b)
    elements.append(Spacer(1, 30))
    
    # Certification
    cert_text = f"""
    I/We hereby certify that the above information is true and correct to the best of my/our knowledge 
    and belief, based on my/our inspection of the project site on _________________.
    """
    elements.append(Paragraph(cert_text, BODY_STYLE))
    elements.append(Spacer(1, 30))
    
    # Signature block
    sig_data = [
        ["", ""],
        ["Architect/Licensed Surveyor", "Place: ________________"],
        [f"Name: {project.get('architect_name', '_________________')}", f"Date: {datetime.now().strftime('%d/%m/%Y')}"],
        [f"License No: {project.get('architect_license', '_________________')}", ""],
    ]
    sig_table = Table(sig_data, colWidths=[3.5*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_form3_pdf(project, buildings, building_costs, estimated_dev_cost, quarter, year):
    """
    FORM-3: Engineer's Certificate - Cost Incurred for Development
    Table A: Building-wise costs
    Table B: Development works costs
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Header
    elements.append(Paragraph("DEPARTMENT OF URBAN DEVELOPMENT", TITLE_STYLE))
    elements.append(Paragraph("GOVERNMENT OF GOA", SUBTITLE_STYLE))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>FORM - 3</b>", SUBTITLE_STYLE))
    elements.append(Paragraph("ENGINEER'S CERTIFICATE", SUBTITLE_STYLE))
    elements.append(Paragraph("(Statement showing cost of construction incurred for development of project)", SMALL_STYLE))
    elements.append(Spacer(1, 12))
    
    # Project Details
    project_info = [
        ["Project Name:", project.get('project_name', ''), "RERA No:", project.get('rera_number', '')],
        ["Promoter:", project.get('promoter_name', ''), "Quarter:", f"{quarter} {year}"],
    ]
    project_table = Table(project_info, colWidths=[1.2*inch, 2.5*inch, 1*inch, 2*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    elements.append(project_table)
    elements.append(Spacer(1, 20))
    
    # Table A: Building-wise Cost
    elements.append(Paragraph("<b>TABLE A: Building-wise Cost of Construction</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    table_a_headers = ["Sr.", "Building/Wing", "Estimated Cost (₹)", "Cost Incurred (₹)", "Balance (₹)", "% Complete"]
    table_a_data = [table_a_headers]
    
    total_estimated = 0
    total_incurred = 0
    
    # Build cost lookup
    cost_lookup = {c.get('building_id'): c for c in building_costs}
    
    for idx, building in enumerate(buildings, 1):
        b_cost = cost_lookup.get(building.get('building_id'), {})
        estimated = building.get('estimated_cost', 0)
        incurred = b_cost.get('cost_incurred', 0)
        balance = estimated - incurred
        pct = (incurred / estimated * 100) if estimated > 0 else 0
        
        total_estimated += estimated
        total_incurred += incurred
        
        row = [
            str(idx),
            building.get('building_name', ''),
            format_currency(estimated),
            format_currency(incurred),
            format_currency(balance),
            f"{pct:.1f}%"
        ]
        table_a_data.append(row)
    
    # Total row
    table_a_data.append([
        "", "TOTAL",
        format_currency(total_estimated),
        format_currency(total_incurred),
        format_currency(total_estimated - total_incurred),
        f"{(total_incurred/total_estimated*100) if total_estimated > 0 else 0:.1f}%"
    ])
    
    table_a = Table(table_a_data, colWidths=[0.4*inch, 1.2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 0.8*inch])
    table_a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table_a)
    elements.append(Spacer(1, 20))
    
    # Table B: Development Works Cost
    elements.append(Paragraph("<b>TABLE B: Cost of Internal/External Development Works</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    infra_cost = estimated_dev_cost.get('infrastructure_cost', 0) if estimated_dev_cost else 0
    
    table_b_data = [
        ["Sr.", "Development Work", "Estimated Cost (₹)", "Cost Incurred (₹)", "Balance (₹)"],
        ["1", "Road, Foot-path and storm water drain", "-", "-", "-"],
        ["2", "Underground sewage drainage network", "-", "-", "-"],
        ["3", "Sewage Treatment Plant", "-", "-", "-"],
        ["4", "Water reservoir/Tank", "-", "-", "-"],
        ["5", "Water distribution network", "-", "-", "-"],
        ["6", "Electric infrastructure", "-", "-", "-"],
        ["7", "Street Lights", "-", "-", "-"],
        ["8", "Entry Gate & Boundary wall", "-", "-", "-"],
        ["9", "Club House", "-", "-", "-"],
        ["10", "Swimming Pool", "-", "-", "-"],
        ["11", "Amphitheatre", "-", "-", "-"],
        ["12", "Gardens / Play Ground", "-", "-", "-"],
        ["", "TOTAL INFRASTRUCTURE", format_currency(infra_cost), "-", "-"],
    ]
    
    table_b = Table(table_b_data, colWidths=[0.4*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1*inch])
    table_b.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table_b)
    elements.append(Spacer(1, 30))
    
    # Certification
    cert_text = """
    I/We hereby certify that the above costs are true and correct to the best of my/our knowledge 
    based on actual expenditure records and site measurements.
    """
    elements.append(Paragraph(cert_text, BODY_STYLE))
    elements.append(Spacer(1, 30))
    
    # Signature
    sig_data = [
        ["Engineer", "Place: ________________"],
        [f"Name: {project.get('engineer_name', '_________________')}", f"Date: {datetime.now().strftime('%d/%m/%Y')}"],
        [f"License No: {project.get('engineer_license', '_________________')}", ""],
    ]
    sig_table = Table(sig_data, colWidths=[3.5*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_form4_pdf(project, project_cost, estimated_dev_cost, quarter, year):
    """
    FORM-4: CA's Certificate - Project Cost and Withdrawal
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Header
    elements.append(Paragraph("DEPARTMENT OF URBAN DEVELOPMENT", TITLE_STYLE))
    elements.append(Paragraph("GOVERNMENT OF GOA", SUBTITLE_STYLE))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>FORM - 4</b>", SUBTITLE_STYLE))
    elements.append(Paragraph("CHARTERED ACCOUNTANT'S CERTIFICATE", SUBTITLE_STYLE))
    elements.append(Paragraph("(Estimated cost of project and amount eligible for withdrawal)", SMALL_STYLE))
    elements.append(Spacer(1, 12))
    
    # Project Details
    project_info = [
        ["Project Name:", project.get('project_name', ''), "RERA No:", project.get('rera_number', '')],
        ["Promoter:", project.get('promoter_name', ''), "Quarter:", f"{quarter} {year}"],
    ]
    project_table = Table(project_info, colWidths=[1.2*inch, 2.5*inch, 1*inch, 2*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    elements.append(project_table)
    elements.append(Spacer(1, 20))
    
    cost = project_cost or {}
    est_dev = estimated_dev_cost or {}
    
    # Section 1: Estimated Cost
    elements.append(Paragraph("<b>1. ESTIMATED COST OF THE PROJECT</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    # 1.i Land Cost
    land_cost = cost.get('estimated_land_cost', 0)
    
    # 1.ii Development Cost breakdown
    buildings_cost = est_dev.get('buildings_cost', 0)
    infra_cost = est_dev.get('infrastructure_cost', 0)
    consultants_fee = est_dev.get('consultants_fee', 0)
    machinery_cost = est_dev.get('machinery_cost', 0)
    total_dev = est_dev.get('total_estimated_development_cost', buildings_cost + infra_cost + consultants_fee + machinery_cost)
    
    cost_data = [
        ["", "Particulars", "Amount (₹)"],
        ["1.i", "LAND COST", format_currency(land_cost)],
        ["", "   a. Land acquisition cost", format_currency(cost.get('land_acquisition_cost', 0))],
        ["", "   b. Development rights premium", format_currency(cost.get('development_rights_premium', 0))],
        ["", "   c. TDR cost", format_currency(cost.get('tdr_cost', 0))],
        ["", "   d. Stamp duty & registration", format_currency(cost.get('stamp_duty', 0))],
        ["", "   e. Government charges", format_currency(cost.get('government_charges', 0))],
        ["1.ii", "DEVELOPMENT COST", format_currency(total_dev)],
        ["", "   1. Buildings cost", format_currency(buildings_cost)],
        ["", "   2. Infrastructure cost", format_currency(infra_cost)],
        ["", "   3. Consultants fee", format_currency(consultants_fee)],
        ["", "   4. Cost of Machineries", format_currency(machinery_cost)],
        ["", "", ""],
        ["", "TOTAL ESTIMATED COST (1.i + 1.ii)", format_currency(land_cost + total_dev)],
    ]
    
    cost_table = Table(cost_data, colWidths=[0.5*inch, 4*inch, 1.8*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, 1), colors.Color(0.9, 0.9, 0.95)),
        ('BACKGROUND', (0, 7), (-1, 7), colors.Color(0.9, 0.9, 0.95)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (1, 1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 7), (1, 7), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 20))
    
    # Section 2: Cost Incurred
    elements.append(Paragraph("<b>2. COST INCURRED TILL DATE</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    total_land_incurred = (
        cost.get('land_acquisition_cost', 0) + cost.get('development_rights_premium', 0) +
        cost.get('tdr_cost', 0) + cost.get('stamp_duty', 0) + cost.get('government_charges', 0)
    )
    total_dev_incurred = cost.get('total_cost_incurred', 0) - total_land_incurred
    
    incurred_data = [
        ["", "Particulars", "Amount (₹)"],
        ["2.i", "Land cost incurred", format_currency(total_land_incurred)],
        ["2.ii", "Development cost incurred", format_currency(total_dev_incurred)],
        ["", "TOTAL COST INCURRED", format_currency(total_land_incurred + total_dev_incurred)],
    ]
    
    incurred_table = Table(incurred_data, colWidths=[0.5*inch, 4*inch, 1.8*inch])
    incurred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(incurred_table)
    elements.append(Spacer(1, 30))
    
    # Certification
    cert_text = """
    I/We hereby certify that the above information is true and correct based on the books of accounts 
    and records maintained by the Promoter.
    """
    elements.append(Paragraph(cert_text, BODY_STYLE))
    elements.append(Spacer(1, 30))
    
    # Signature
    sig_data = [
        ["Chartered Accountant", "Place: ________________"],
        [f"Name: {project.get('ca_name', '_________________')}", f"Date: {datetime.now().strftime('%d/%m/%Y')}"],
        [f"Firm: {project.get('ca_firm_name', '_________________')}", ""],
        [f"Membership No: {project.get('ca_membership_number', '_________________')}", ""],
    ]
    sig_table = Table(sig_data, colWidths=[3.5*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_annexure_a_pdf(project, sales, buildings, quarter, year):
    """
    Annexure-A: Statement of Sales and Receivables
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Header
    elements.append(Paragraph("ANNEXURE - A", TITLE_STYLE))
    elements.append(Paragraph("STATEMENT OF SALES AND RECEIVABLES", SUBTITLE_STYLE))
    elements.append(Spacer(1, 12))
    
    # Project Details
    project_info = [
        ["Project:", project.get('project_name', ''), "RERA No:", project.get('rera_number', ''), "Quarter:", f"{quarter} {year}"],
    ]
    project_table = Table(project_info, colWidths=[0.8*inch, 2.5*inch, 0.8*inch, 2*inch, 0.8*inch, 1*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTNAME', (4, 0), (4, 0), 'Helvetica-Bold'),
    ]))
    elements.append(project_table)
    elements.append(Spacer(1, 15))
    
    # Sales Table
    headers = ["Sr.", "Unit No.", "Building", "Carpet\nArea (sqm)", "Buyer Name", "Agreement\nDate", 
               "Sale Value (₹)", "Received (₹)", "Balance (₹)"]
    table_data = [headers]
    
    total_sale_value = 0
    total_received = 0
    total_balance = 0
    
    for idx, sale in enumerate(sales, 1):
        sale_value = sale.get('sale_value', 0)
        received = sale.get('amount_received', 0)
        balance = sale_value - received
        
        total_sale_value += sale_value
        total_received += received
        total_balance += balance
        
        row = [
            str(idx),
            sale.get('unit_number', ''),
            sale.get('building_name', ''),
            f"{sale.get('carpet_area', 0):.2f}",
            sale.get('buyer_name', '-'),
            format_date(sale.get('agreement_date', '')),
            format_currency(sale_value),
            format_currency(received),
            format_currency(balance)
        ]
        table_data.append(row)
    
    # Total row
    table_data.append([
        "", "TOTAL", "", "", "", "",
        format_currency(total_sale_value),
        format_currency(total_received),
        format_currency(total_balance)
    ])
    
    col_widths = [0.4*inch, 0.8*inch, 0.8*inch, 0.7*inch, 1.8*inch, 0.9*inch, 1.1*inch, 1.1*inch, 1.1*inch]
    sales_table = Table(table_data, colWidths=col_widths)
    sales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (6, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(sales_table)
    elements.append(Spacer(1, 20))
    
    # Summary
    summary_data = [
        ["Summary:", ""],
        ["Total Units Sold:", str(len(sales))],
        ["Total Sale Value:", format_currency(total_sale_value)],
        ["Total Amount Received:", format_currency(total_received)],
        ["Total Balance Receivable:", format_currency(total_balance)],
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(summary_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
