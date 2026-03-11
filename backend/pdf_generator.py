"""
RERA Forms PDF Generator - Goa State Official Format
Generates Form-1 to Form-6 and Annexure-A in official Goa RERA format
Based on: Goa Real Estate (Regulation and Development) Rules 2017
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

# Custom styles for official format
TITLE_STYLE = ParagraphStyle(
    'Title',
    parent=styles['Heading1'],
    fontSize=12,
    alignment=TA_CENTER,
    spaceAfter=6,
    fontName='Helvetica-Bold'
)

SUBTITLE_STYLE = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=10,
    alignment=TA_CENTER,
    spaceAfter=4,
    fontName='Helvetica-Bold'
)

HEADER_STYLE = ParagraphStyle(
    'Header',
    parent=styles['Normal'],
    fontSize=9,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

BODY_STYLE = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=9,
    alignment=TA_JUSTIFY,
    fontName='Helvetica',
    leading=12
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

RULE_STYLE = ParagraphStyle(
    'Rule',
    parent=styles['Normal'],
    fontSize=8,
    alignment=TA_CENTER,
    fontName='Helvetica-Oblique'
)

def format_currency(amount):
    """Format number as Indian currency with lakh/crore separators"""
    if amount is None or amount == 0:
        return "₹0"
    return "₹" + format_indian_number(amount)

def format_indian_number(num):
    """Format number in Indian numbering system (lakhs, crores)
    Example: 7100000 -> 71,00,000
             55195000 -> 5,51,95,000
    """
    if num is None or num == 0:
        return "0"
    
    num = int(num)
    is_negative = num < 0
    num = abs(num)
    
    s = str(num)
    
    if len(s) <= 3:
        result = s
    else:
        # Last 3 digits
        result = s[-3:]
        s = s[:-3]
        # Then groups of 2
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
    
    return "-" + result if is_negative else result

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
    Official Goa RERA Format as per Rule 5(1)(a)(ii)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch, 
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    start_date, end_date = get_quarter_dates(quarter, year)
    
    # Header - Official Format
    elements.append(Paragraph("The Goa Real Estate (Regulation and Development)", SMALL_STYLE))
    elements.append(Paragraph("(Registration of Real Estate Projects, Registration of Real Estate Agents,", SMALL_STYLE))
    elements.append(Paragraph("Rates of Interest and Disclosures on Website) Rules 2017", SMALL_STYLE))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("<b>FORM 1</b>", TITLE_STYLE))
    elements.append(Paragraph("<i>(See Rule 5 (1) (a) (ii))</i>", RULE_STYLE))
    elements.append(Paragraph("<b>ARCHITECT'S / LICENSED SURVEYOR'S CERTIFICATE</b>", SUBTITLE_STYLE))
    elements.append(Paragraph("(To be submitted at the time of Registration of On-going Project", SMALL_STYLE))
    elements.append(Paragraph("and for withdrawal of Money from Designated Account)", SMALL_STYLE))
    elements.append(Spacer(1, 15))
    
    # To section
    to_text = f"""<b>To</b><br/>
    {project.get('promoter_name', '________________________')},<br/>
    {project.get('promoter_address', project.get('project_address', '________________________'))},<br/>
    {project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}
    """
    elements.append(Paragraph(to_text, BODY_STYLE))
    elements.append(Spacer(1, 8))
    
    # Date
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", RIGHT_STYLE))
    elements.append(Spacer(1, 10))
    
    # Subject line
    num_buildings = len(buildings) if buildings else "__"
    phase = project.get('project_phase', '1')
    subject_text = f"""<b>Subject:</b> Certificate of Percentage of Completion of Construction Work of 
    <b>{num_buildings}</b> Building(s) / Wing(s) of the <b>{phase}</b> Phase of the Project situated on the Plot bearing 
    Survey No./Plot No. <b>{project.get('survey_number', '________')}</b> of Ward <b>{project.get('ward', '________')}</b> 
    Municipality <b>{project.get('municipality', '________')}</b> District <b>{project.get('district', 'North Goa')}</b> 
    PIN <b>{project.get('pin_code', '________')}</b> village/panchayat <b>{project.get('village', '________')}</b> 
    taluka <b>{project.get('taluka', '________')}</b> admeasuring <b>{project.get('plot_area', '________')}</b> sq.mts. 
    area being developed by <b>{project.get('promoter_name', '________')}</b>
    """
    elements.append(Paragraph(subject_text, BODY_STYLE))
    elements.append(Spacer(1, 8))
    
    # Reference
    elements.append(Paragraph(f"<b>Ref: Goa RERA Registration Number:</b> {project.get('rera_number', '_________________________')}", BODY_STYLE))
    elements.append(Spacer(1, 10))
    
    # Salutation
    elements.append(Paragraph("<b>Sir,</b>", BODY_STYLE))
    elements.append(Spacer(1, 8))
    
    # Assignment statement
    architect_name = project.get('architect_name', '________________________')
    assignment_text = f"""I/We <b>{architect_name}</b> have undertaken assignment as Architect / Licensed Surveyor 
    of certifying Percentage of Completion of Construction Work of the <b>{num_buildings}</b> Building(s) / Wing(s) 
    of the <b>{phase}</b> Phase of the Project, situated on the plot bearing Survey No./Plot No. 
    <b>{project.get('survey_number', '________')}</b> of Ward <b>{project.get('ward', '________')}</b> 
    Municipality/Village <b>{project.get('village', '________')}</b> District <b>{project.get('district', 'North Goa')}</b> 
    admeasuring <b>{project.get('plot_area', '________')}</b> sq.mts. area being developed by 
    <b>{project.get('promoter_name', '________')}</b>.
    """
    elements.append(Paragraph(assignment_text, BODY_STYLE))
    elements.append(Spacer(1, 12))
    
    # Technical Professionals Section
    elements.append(Paragraph("<b>1. Following technical professionals are appointed by Owner / Promoter:-</b>", BODY_STYLE))
    elements.append(Spacer(1, 6))
    
    professionals = [
        [f"(i) M/s/Shri/Smt. {project.get('architect_name', '________________________')} as Architect;"],
        [f"(ii) M/s/Shri/Smt. {project.get('structural_consultant_name', '________________________')} as Structural Consultant;"],
        [f"(iii) M/s/Shri/Smt. {project.get('mep_consultant_name', '________________________')} as MEP Consultant;"],
        [f"(iv) M/s/Shri/Smt. {project.get('site_supervisor_name', '________________________')} as Site Supervisor;"],
    ]
    
    prof_table = Table(professionals, colWidths=[6.5*inch])
    prof_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(prof_table)
    elements.append(Spacer(1, 12))
    
    # Certification text
    cert_intro = f"""Based on Site Inspection, with respect to each of the Building/Wing of the aforesaid Real Estate Project, 
    I certify that as on the date of this certificate, the Percentage of Work done for each of the building/Wing of the 
    Real Estate Project as registered vide number <b>{project.get('rera_number', '________')}</b> under GoaRERA is as per 
    Table A herein below. The percentage of the work executed with respect to each of the activity of the entire phase 
    is detailed in Table B.
    """
    elements.append(Paragraph(cert_intro, BODY_STYLE))
    elements.append(Spacer(1, 15))
    
    # Build progress lookup
    progress_lookup = {p.get('building_id'): p for p in construction_progress} if construction_progress else {}
    
    # TABLE A - For each building
    for building in (buildings or []):
        building_name = building.get('building_name', 'Building')
        elements.append(Paragraph(f"<b>TABLE A: Building / Wing Number: {building_name}</b>", HEADER_STYLE))
        elements.append(Spacer(1, 6))
        
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
        carpark = tower_acts.get('carpark', {})
        handover = tower_acts.get('handover_intimation', {})
        
        def get_activity_completion(cat_data, activity_id):
            if not cat_data:
                return 0
            activity = cat_data.get(activity_id, {})
            return activity.get('completion', 0) if isinstance(activity, dict) else 0
        
        def get_cat_avg(cat_data):
            if not cat_data:
                return 0
            total = sum(v.get('completion', 0) for v in cat_data.values() if isinstance(v, dict))
            count = sum(1 for v in cat_data.values() if isinstance(v, dict))
            return total / count if count > 0 else 0
        
        # Official Form-1 Table A format
        num_basements = building.get('basements', 0)
        num_podiums = building.get('podiums', 0)
        num_floors = building.get('residential_floors', 4)
        
        table_a_data = [
            ["Sr. No", "Tasks/Activity", "Percentage of\nwork done"],
            ["1", "Excavation", f"{get_activity_completion(plinth, 'excavation'):.0f}%"],
            ["2", f"{num_basements} number of Basement(s) and Plinth", f"{get_cat_avg(plinth):.0f}%"],
            ["3", f"{num_podiums} number of Podiums", f"{get_cat_avg(plinth):.0f}%" if num_podiums > 0 else "N/A"],
            ["4", "Stilt Floor", f"{get_activity_completion(plinth, 'filling_earth_plinth_pcc'):.0f}%"],
            ["5", f"{num_floors} number of Slabs of Super Structure", f"{get_cat_avg(slab):.0f}%"],
            ["6", "Internal walls, Internal Plaster, Floorings within Flats/Premises", f"{get_cat_avg(brickwork):.0f}%"],
            ["7", "Doors and Windows to each of the Flat/Premises", f"{(get_cat_avg(doors) + get_cat_avg(windows)) / 2:.0f}%"],
            ["8", "Sanitary Fittings within the Flat/Premises, Electrical Fittings", f"{(get_cat_avg(plumbing) + get_cat_avg(electrical)) / 2:.0f}%"],
            ["9", "Staircases, Lift Wells and Lobbies, Water Tanks", f"{get_cat_avg(slab):.0f}%"],
            ["10", "External plumbing/plaster, Elevation, Terraces waterproofing,\nLifts, Fire Fighting, Electrical to Common Areas, etc.", f"{(get_cat_avg(waterproof) + get_cat_avg(painting)) / 2:.0f}%"],
        ]
        
        table_a = Table(table_a_data, colWidths=[0.6*inch, 4.5*inch, 1.2*inch])
        table_a.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table_a)
        elements.append(Spacer(1, 10))
        
        # Add overall completion for this building
        overall = progress.get('overall_completion', 0)
        elements.append(Paragraph(f"<b>Overall Completion for {building_name}: {overall:.1f}%</b>", SMALL_STYLE))
        elements.append(Spacer(1, 15))
    
    # TABLE B - Infrastructure/Common Development Works
    elements.append(PageBreak())
    elements.append(Paragraph("<b>TABLE B: Internal & External Development Works in Respect of the entire Registered Phase</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    infra_data = infrastructure_progress.get('activities', {}) if infrastructure_progress else {}
    
    # Official Form-1 Table B format
    table_b_data = [
        ["Sr. No.", "Common areas and Facilities, Amenities", "Proposed\n(Yes/No)", "Percentage of\nwork done", "Details"],
        ["1.", "Internal Roads & Footpaths", "Yes", f"{infra_data.get('road_footpath_storm_drain', {}).get('completion', 0):.0f}%", ""],
        ["2.", "Water Supply", "Yes", f"{infra_data.get('underground_water_distribution', {}).get('completion', 0):.0f}%", ""],
        ["3.", "Sewerage (chamber, lines, Septic Tank, STP)", "Yes", f"{infra_data.get('underground_sewage_network', {}).get('completion', 0):.0f}%", ""],
        ["4.", "Storm Water Drains", "Yes", f"{infra_data.get('road_footpath_storm_drain', {}).get('completion', 0):.0f}%", ""],
        ["5.", "Landscaping & Tree Planting", "Yes", f"{infra_data.get('gardens_playground', {}).get('completion', 0):.0f}%", ""],
        ["6.", "Street Lighting", "Yes", f"{infra_data.get('street_lights', {}).get('completion', 0):.0f}%", ""],
        ["7.", "Community Buildings (Club House)", "Yes", f"{infra_data.get('club_house', {}).get('completion', 0):.0f}%", ""],
        ["8.", "Treatment and disposal of sewage and sullage water", "Yes", f"{infra_data.get('sewage_treatment_plant', {}).get('completion', 0):.0f}%", ""],
        ["9.", "Solid Waste management & Disposal", "Yes", "0%", ""],
        ["10.", "Water conservation, Rain water harvesting", "Yes", f"{infra_data.get('overhead_sump_reservoir', {}).get('completion', 0):.0f}%", ""],
        ["11.", "Energy management", "Yes", f"{infra_data.get('electric_substation_cables', {}).get('completion', 0):.0f}%", ""],
        ["12.", "Fire protection and fire safety requirements", "Yes", "0%", ""],
        ["13.", "Electrical meter room, sub-station, receiving station", "Yes", f"{infra_data.get('electric_substation_cables', {}).get('completion', 0):.0f}%", ""],
        ["14.", "Swimming Pool", "Yes", f"{infra_data.get('swimming_pool', {}).get('completion', 0):.0f}%", ""],
        ["15.", "Amphitheatre", "Yes", f"{infra_data.get('amphitheatre', {}).get('completion', 0):.0f}%", ""],
        ["16.", "Boundary Wall & Entry Gate", "Yes", f"{(infra_data.get('boundary_wall', {}).get('completion', 0) + infra_data.get('entry_gate', {}).get('completion', 0)) / 2:.0f}%", ""],
    ]
    
    table_b = Table(table_b_data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 0.9*inch, 1*inch])
    table_b.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table_b)
    elements.append(Spacer(1, 25))
    
    # Closing
    elements.append(Paragraph("<b>Yours Faithfully,</b>", BODY_STYLE))
    elements.append(Spacer(1, 30))
    
    # Signature block
    sig_data = [
        ["_______________________________", ""],
        ["Signature & Name (IN BLOCK LETTERS)", ""],
        ["of Architect / Licensed Surveyor", ""],
        [f"Name: {project.get('architect_name', '________________________')}", ""],
        [f"License No.: {project.get('architect_license', '________________________')}", ""],
    ]
    sig_table = Table(sig_data, colWidths=[4*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_form3_pdf(project, buildings, construction_progress, infrastructure_progress, estimated_dev_cost, quarter, year):
    """
    FORM-3: Engineer's Certificate - Cost Incurred for Development
    Cost Incurred = (% Work Completed from Construction Progress) × (Estimated Cost per Building)
    Official Goa RERA Format as per Rule 5(1)(a)(ii)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []

    # Header
    elements.append(Paragraph("The Goa Real Estate (Regulation and Development)", SMALL_STYLE))
    elements.append(Paragraph("(Registration of Real Estate Projects, Registration of Real Estate Agents,", SMALL_STYLE))
    elements.append(Paragraph("Rates of Interest and Disclosures on Website) Rules 2017", SMALL_STYLE))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>FORM 3</b>", TITLE_STYLE))
    elements.append(Paragraph("<i>(See Rule 5 (1) (a) (ii))</i>", RULE_STYLE))
    elements.append(Paragraph("<b>ENGINEER'S CERTIFICATE</b>", SUBTITLE_STYLE))
    elements.append(Paragraph("(Cost Incurred Statement for Development)", SMALL_STYLE))
    elements.append(Spacer(1, 15))

    # To section
    to_text = f"""<b>To</b><br/>
    {project.get('promoter_name', '________________________')},<br/>
    {project.get('promoter_address', project.get('project_address', '________________________'))},<br/>
    {project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}
    """
    elements.append(Paragraph(to_text, BODY_STYLE))
    elements.append(Spacer(1, 8))

    # Date
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", RIGHT_STYLE))
    elements.append(Spacer(1, 10))

    # Subject
    subject_text = f"""<b>Subject:</b> Certificate of Cost Incurred for Development of the Project
    <b>{project.get('project_name', '________')}</b> situated at {project.get('village', '________')},
    {project.get('taluka', '________')}, {project.get('district', 'North Goa')}
    """
    elements.append(Paragraph(subject_text, BODY_STYLE))
    elements.append(Spacer(1, 8))

    # Reference
    elements.append(Paragraph(f"<b>Ref: Goa RERA Registration Number:</b> {project.get('rera_number', '_________________________')}", BODY_STYLE))
    elements.append(Spacer(1, 10))

    # Salutation
    elements.append(Paragraph("<b>Sir,</b>", BODY_STYLE))
    elements.append(Spacer(1, 8))

    # Assignment statement
    engineer_name = project.get('engineer_name', '________________________')
    assignment_text = f"""I/We <b>{engineer_name}</b> have undertaken assignment as Engineer for certifying
    Cost Incurred for Development of the Project <b>{project.get('project_name', '________')}</b>
    as registered vide number <b>{project.get('rera_number', '________')}</b> under GoaRERA.
    """
    elements.append(Paragraph(assignment_text, BODY_STYLE))
    elements.append(Spacer(1, 12))

    # TABLE A - Building-wise Cost
    # Cost Incurred = (overall_completion % from Construction Progress) × Estimated Cost
    elements.append(Paragraph("<b>TABLE A: Cost Incurred for Building Construction</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))

    cp_lookup = {cp.get('building_id'): cp for cp in (construction_progress or [])}
    est_cost = estimated_dev_cost or {}

    table_a_data = [
        ["Sr.", "Building/Wing", "% Complete", "Estimated Cost (₹)", "Cost Incurred (₹)", "Balance (₹)"]
    ]

    total_estimated = 0
    total_incurred = 0

    for idx, building in enumerate(buildings or [], 1):
        progress = cp_lookup.get(building.get('building_id'), {})
        completion_pct = progress.get('overall_completion', 0)
        est = building.get('estimated_cost', 0)
        incurred = round((completion_pct / 100) * est)
        balance = est - incurred

        total_estimated += est
        total_incurred += incurred

        table_a_data.append([
            str(idx),
            building.get('building_name', ''),
            f"{completion_pct:.1f}%",
            format_indian_number(est),
            format_indian_number(incurred),
            format_indian_number(balance)
        ])

    table_a_data.append([
        "", "TOTAL", "",
        format_indian_number(total_estimated),
        format_indian_number(total_incurred),
        format_indian_number(total_estimated - total_incurred)
    ])

    table_a = Table(table_a_data, colWidths=[0.4*inch, 1.5*inch, 0.7*inch, 1.4*inch, 1.4*inch, 1.2*inch])
    table_a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table_a)
    elements.append(Spacer(1, 15))

    # TABLE B - Development Works Cost
    # Infra Cost Incurred = (overall_completion % from Infrastructure Progress) × Estimated Infra Cost
    elements.append(Paragraph("<b>TABLE B: Cost of Internal/External Development Works</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))

    infra_cost = est_cost.get('infrastructure_cost', 0)
    infra_completion = (infrastructure_progress or {}).get('overall_completion', 0)
    infra_incurred = round((infra_completion / 100) * infra_cost)
    infra_balance = infra_cost - infra_incurred

    table_b_data = [
        ["Sr.", "Development Work", "Estimated (₹)", "Incurred (₹)", "Balance (₹)"],
        ["1", "Internal Roads & Footpaths", "-", "-", "-"],
        ["2", "Water Supply & Distribution", "-", "-", "-"],
        ["3", "Sewerage & STP", "-", "-", "-"],
        ["4", "Storm Water Drains", "-", "-", "-"],
        ["5", "Landscaping", "-", "-", "-"],
        ["6", "Street Lighting", "-", "-", "-"],
        ["7", "Club House", "-", "-", "-"],
        ["8", "Swimming Pool", "-", "-", "-"],
        ["9", "Electrical Infrastructure", "-", "-", "-"],
        ["10", "Boundary Wall & Gate", "-", "-", "-"],
        ["", "TOTAL INFRASTRUCTURE",
         format_indian_number(infra_cost),
         format_indian_number(infra_incurred),
         format_indian_number(infra_balance)],
    ]

    table_b = Table(table_b_data, colWidths=[0.5*inch, 2.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table_b.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table_b)
    elements.append(Spacer(1, 25))
    
    # Closing
    elements.append(Paragraph("<b>Yours Faithfully,</b>", BODY_STYLE))
    elements.append(Spacer(1, 30))
    
    # Signature block
    sig_data = [
        ["_______________________________", ""],
        ["Signature & Name of Engineer", ""],
        [f"Name: {project.get('engineer_name', '________________________')}", ""],
        [f"License No.: {project.get('engineer_license', '________________________')}", ""],
    ]
    sig_table = Table(sig_data, colWidths=[4*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_form4_pdf(project, form4_data, quarter, year):
    """
    FORM-4: Chartered Accountant's Certificate - CA Certificate format.
    Matches the Excel CA Certificate format exactly:
    Columns: Sr No / Particulars / Estimated Amount in Rs. / Incurred Amount in Rs.
    form4_data is a pre-computed dict from server._build_form4_data().
    """
    buffer = BytesIO()
    # Use landscape A4 to give more width for the 4-column table
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.4*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []

    fd = form4_data or {}

    # Unpack all pre-computed values
    lc_a_est      = fd.get("lc_a_est", 0);    lc_a_inc      = fd.get("lc_a_inc", 0)
    lc_b_est      = fd.get("lc_b_est", 0);    lc_b_inc      = fd.get("lc_b_inc", 0)
    lc_c_est      = fd.get("lc_c_est", 0);    lc_c_inc      = fd.get("lc_c_inc", 0)
    lc_d_est      = fd.get("lc_d_est", 0);    lc_d_inc      = fd.get("lc_d_inc", 0)
    lc_e_est      = fd.get("lc_e_est", 0);    lc_e_inc      = fd.get("lc_e_inc", 0)
    rehab_i_est   = fd.get("rehab_i_est", 0); rehab_i_inc   = fd.get("rehab_i_inc", 0)
    rehab_ii_inc  = fd.get("rehab_ii_inc", 0)
    rehab_iii_inc = fd.get("rehab_iii_inc", 0)
    rehab_iv_inc  = fd.get("rehab_iv_inc", 0)
    rehab_any     = fd.get("rehab_any", False)
    land_sub_est  = fd.get("land_sub_est", 0); land_sub_inc  = fd.get("land_sub_inc", 0)
    dev_a1_est    = fd.get("dev_a1_est", 0)
    dev_a2_inc    = fd.get("dev_a2_inc", 0)
    dev_a3_est    = fd.get("dev_a3_est", 0);   dev_a3_inc    = fd.get("dev_a3_inc", 0)
    dev_b_est     = fd.get("dev_b_est", 0);    dev_b_inc     = fd.get("dev_b_inc", 0)
    dev_c_est     = fd.get("dev_c_est", 0);    dev_c_inc     = fd.get("dev_c_inc", 0)
    dev_sub_est   = fd.get("dev_sub_est", 0);  dev_sub_inc   = fd.get("dev_sub_inc", 0)
    total_est     = fd.get("total_est", 0);    total_inc     = fd.get("total_inc", 0)
    arch_pct      = fd.get("arch_pct", 0)
    proportion    = fd.get("proportion", 0)
    withdraw_allow = fd.get("withdraw_allow", 0)
    withdrawn_td  = fd.get("withdrawn_td", 0)
    net_withdraw  = fd.get("net_withdraw", 0)
    bal_cost         = fd.get("bal_cost", 0)
    bal_recv_sold    = fd.get("bal_recv_sold", 0)
    unsold_area      = fd.get("unsold_area", 0)
    asr_rate         = fd.get("asr_rate", 0)
    avg_sale_price   = fd.get("avg_sale_price", 0)
    total_sale_val_sold = fd.get("total_sale_val_sold", 0)
    unsold_val       = fd.get("unsold_val", 0)
    total_recv       = fd.get("total_recv", 0)
    deposit_pct      = fd.get("deposit_pct", 0.70)
    deposit_amt      = fd.get("deposit_amt", 0)
    sales            = fd.get("sales", [])
    buildings        = fd.get("buildings", [])
    building_map     = fd.get("building_map", {})

    # ── Colour helpers ────────────────────────────────────────────────────────
    C_TITLE   = colors.Color(0x1F/255, 0x38/255, 0x64/255)  # dark navy
    C_SECTION = colors.Color(0xD9/255, 0xE1/255, 0xF2/255)  # light blue
    C_SUBTOT  = colors.Color(0xFC/255, 0xE4/255, 0xD6/255)  # peach
    C_SUMMARY = colors.Color(0xE2/255, 0xEF/255, 0xDA/255)  # light green
    C_NET     = colors.Color(1.0, 1.0, 0)                   # yellow
    C_NOTE    = colors.Color(1.0, 0.98/255*250, 0.80)       # light yellow
    C_WHITE   = colors.white
    C_BLACK   = colors.black

    # ── Column widths (Sr / Particulars / Estimated / Incurred) ───────────────
    CW = [0.45*inch, 3.8*inch, 1.45*inch, 1.45*inch]
    TW = sum(CW)

    # ── Local style helpers ───────────────────────────────────────────────────
    def _ps(size=8, bold=False, align=TA_LEFT, color=None):
        st = ParagraphStyle('_', parent=styles['Normal'],
                            fontSize=size, leading=size * 1.2,
                            alignment=align, fontName='Helvetica-Bold' if bold else 'Helvetica')
        if color:
            st.textColor = color
        return st

    def _fmtv(val, decimals=False):
        """Format numeric value or return 'NA'."""
        if not val:
            return "NA"
        v = float(val)
        if decimals:
            return f"{v:,.2f}"
        return format_indian_number(int(v))

    def _p(text, size=8, bold=False, align=TA_LEFT, color=None):
        return Paragraph(text, _ps(size, bold, align, color))

    def _cell(text, size=8, bold=False, align=TA_CENTER, bg=None, fg=C_BLACK, wrap=True):
        """Build a one-cell paragraph string; used inside Table data lists."""
        return text  # tables accept strings; we set style via TableStyle

    # ── Build the master rows list ─────────────────────────────────────────────
    # Each entry = [sr, particulars, estimated, incurred]
    # Special marker dicts control merge/colour per row.

    # We'll build a reportlab Table with style commands
    rows = []
    style_cmds = []

    def r_idx():
        return len(rows)

    def add_row(sr, part, est, inc):
        rows.append([str(sr) if sr is not None else "", part, est, inc])

    def fv(val, dec=False):
        if val is None or val == "NA":
            return "NA"
        if isinstance(val, str):
            return val
        if not val:
            return "NA"
        if dec:
            return f"{float(val):,.2f}"
        return format_indian_number(int(val))

    def fpct(val):
        if not val:
            return "NA"
        return f"{float(val)*100:.2f}%"

    # ── Row 0: Title ─────────────────────────────────────────────
    rows.append(["Form-4: CA Certificate", "", "", ""])
    style_cmds += [
        ('SPAN', (0, 0), (3, 0)),
        ('BACKGROUND', (0, 0), (3, 0), C_TITLE),
        ('TEXTCOLOR', (0, 0), (3, 0), C_WHITE),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 12),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('VALIGN', (0, 0), (3, 0), 'MIDDLE'),
    ]

    # ── Row 1: Subtitle ──────────────────────────────────────────
    rows.append(["(FOR REGISTRATION OF A PROJECT AND SUBSEQUENT WITHDRAWAL OF MONEY)", "", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (0, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_TITLE),
        ('TEXTCOLOR', (0, r), (3, r), C_WHITE),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    # ── Row 2: Project info strip ─────────────────────────────────
    proj_info = (f"Project: {project.get('project_name','—')}   |   RERA No.: {project.get('rera_number','—')}"
                 f"   |   Period: {quarter} {year}   |   Date: {datetime.now().strftime('%d/%m/%Y')}")
    rows.append([proj_info, "", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (0, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTSIZE', (0, r), (3, r), 8),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    # ── Row 3: Column headers ─────────────────────────────────────
    rows.append(["Sr No", "Particulars", "Estimated Amount\nin Rs.", "Incurred Amount\nin Rs."])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
        ('ROWBACKGROUNDS', (0, r), (3, r), [C_SECTION]),
    ]

    # ── Section header: Land Cost ──────────────────────────────────
    rows.append(["", "i.  Land Cost :", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (1, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTNAME', (1, r), (1, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
    ]

    # ── Land cost sub-items ───────────────────────────────────────
    def add_item_row(sr, text, est_val, inc_val, bg=None, note=False):
        r_i = r_idx()
        rows.append([sr if sr is not None else "1", text,
                     fv(est_val), fv(inc_val, dec=True)])
        cmds = [
            ('FONTSIZE', (0, r_i), (3, r_i), 8),
            ('ALIGN', (2, r_i), (3, r_i), 'RIGHT'),
        ]
        if sr is not None and sr != "":
            cmds.append(('ALIGN', (0, r_i), (0, r_i), 'CENTER'))
        if bg:
            cmds.append(('BACKGROUND', (0, r_i), (3, r_i), bg))
        if note:
            cmds.append(('FONTNAME', (0, r_i), (3, r_i), 'Helvetica-Oblique'))
        style_cmds.extend(cmds)

    add_item_row(1,
        "a. Acquisition Cost of Land or Development Rights, lease Premium, lease rent, "
        "interest cost incurred or payable on Land Cost and legal cost.",
        lc_a_est, lc_a_inc)

    add_item_row("",
        "b. Amount of Premium payable to obtain development rights, FSI, additional FSI, "
        "fungible area, and any other incentive under DCR from Local Authority or State "
        "Government or any Statutory Authority.",
        lc_b_est, lc_b_inc)

    add_item_row("", "c. Acquisition cost of TDR (if any)", lc_c_est, lc_c_inc)

    add_item_row("",
        "d. Amounts payable to State Government or competent authority or any other statutory "
        "authority of the State or Central Government, towards stamp duty, transfer charges, "
        "registration fees etc; and",
        lc_d_est, lc_d_inc)

    add_item_row("",
        "e. Land Premium payable as per annual statement of rates (ASR) for redevelopment "
        "of land owned by public authorities.",
        lc_e_est, lc_e_inc)

    # f. Rehabilitation sub-header
    rows.append(["", "f. Under Rehabilitation Scheme :", "", ""])
    r = r_idx() - 1
    style_cmds += [('FONTNAME', (1, r), (1, r), 'Helvetica-Bold'), ('FONTSIZE', (0, r), (3, r), 8)]

    add_item_row("",
        "   (i) Estimated construction cost of rehab building including site development "
        "and infrastructure for the same as certified by Engineer.",
        rehab_i_est if rehab_any else "NA",
        rehab_i_inc if rehab_any else "NA")

    add_item_row("",
        "   (ii) Actual Cost of construction of rehab building incurred as per the books "
        "of accounts as verified by the CA.",
        "NA",
        rehab_ii_inc if rehab_any else "NA")

    # Note row
    rows.append(["", "Note: (for total cost of construction incurred, Minimum of (i) or (ii) is to be considered).",
                 "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (1, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_NOTE),
        ('FONTNAME', (1, r), (1, r), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, r), (3, r), 7),
    ]

    add_item_row("",
        "   (iii) Cost towards clearance of land of all or any encumbrances including cost of "
        "removal of legal/illegal occupants, cost for providing temporary transit accommodation "
        "or rent in lieu of Transit Accommodation, overhead cost,",
        "NA", rehab_iii_inc if rehab_any else "NA")

    add_item_row("",
        "   (iv) Cost of ASR linked premium, fees, charges and security deposits or maintenance "
        "deposit, or any amount whatsoever payable to any authorities towards and in project of "
        "rehabilitation.",
        "NA", rehab_iv_inc if rehab_any else "NA")

    # Land Sub-total
    rows.append(["", "Sub-Total of LAND COST",
                 fv(land_sub_est), fv(land_sub_inc, dec=True)])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SUBTOT),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
        ('ALIGN', (2, r), (3, r), 'RIGHT'),
    ]

    # ── Section: Development Cost ─────────────────────────────────
    rows.append(["", "ii.  Development Cost / Cost of Construction :", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (1, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTNAME', (1, r), (1, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
    ]

    # a(i) Estimated construction cost
    add_item_row("",
        "a. (i) Estimated Cost of Construction as certified by Engineer.",
        dev_a1_est, "Refer Note")

    # a(ii) Actual construction cost
    add_item_row("",
        "   (ii) Actual Cost of construction incurred as per the books of accounts "
        "as verified by the CA.",
        "Refer Note", dev_a2_inc)

    # MIN note
    rows.append(["",
        "Note: (for adding to total cost of construction incurred, Minimum of (i) or (ii) is to be considered).",
        "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (1, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_NOTE),
        ('FONTNAME', (1, r), (1, r), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, r), (3, r), 7),
    ]

    # a(iii) On-site expenditure
    add_item_row("",
        "(iii) On-site expenditure for development of entire project excluding cost of "
        "construction as per (i) or (ii) above, i.e. salaries, consultants fees, site "
        "overheads, development works, cost of services (including water, electricity, "
        "sewerage, drainage, layout roads etc.), cost of machineries and equipment "
        "including its hire and maintenance costs, consumables etc.",
        dev_a3_est, dev_a3_inc)

    # b. Taxes
    add_item_row("",
        "b. Payment of Taxes, cess, fees, charges, premiums, interest etc. "
        "to any statutory Authority.",
        dev_b_est, dev_b_inc)

    # c. Finance cost
    add_item_row("",
        "c. Principal sum and interest payable to financial institutions, scheduled banks, "
        "non-banking financial institution (NBFC) or money lenders on construction funding "
        "or money borrowed for construction;",
        dev_c_est, dev_c_inc)

    # Dev Sub-total
    rows.append(["", "Sub-Total of Development Cost",
                 fv(dev_sub_est), fv(dev_sub_inc, dec=True)])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SUBTOT),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
        ('ALIGN', (2, r), (3, r), 'RIGHT'),
    ]

    # ── Summary rows Sr 2-8 ───────────────────────────────────────
    def add_summary_row(sr, text, est_val, inc_val, net=False):
        r_i = r_idx()
        rows.append([str(sr), text, est_val or "", inc_val or ""])
        bg = C_NET if net else C_SUMMARY
        style_cmds.extend([
            ('BACKGROUND', (0, r_i), (3, r_i), bg),
            ('FONTNAME', (0, r_i), (3, r_i), 'Helvetica-Bold' if net else 'Helvetica'),
            ('FONTSIZE', (0, r_i), (3, r_i), 8),
            ('ALIGN', (0, r_i), (0, r_i), 'CENTER'),
            ('ALIGN', (2, r_i), (3, r_i), 'RIGHT'),
        ])

    add_summary_row(2,
        "Total Estimated Cost of the Real Estate Project [1(i) + 1(ii)] of Estimated Column.",
        fv(total_est), "")

    add_summary_row(3,
        "Total Cost Incurred of the Real Estate Project [1(i) + 1(ii)] of Incurred Column.",
        "", fv(total_inc, dec=True))

    add_summary_row(4,
        "% Completion of Construction Work (as per Project Architect's Certificate)",
        "", fpct(arch_pct))

    add_summary_row(5,
        f"Proportion of the Cost incurred on Land Cost and {arch_pct*100:.2f}% "
        f"Construction Cost to the Total Estimated Cost.  (Sr.3 / Sr.2 %)",
        "", fpct(proportion))

    add_summary_row(6,
        "Amount Which can be Withdrawn from the Designated Account. "
        "(Total Estimated Cost × Proportion of cost incurred  =  Sr.2 × Sr.5)",
        "", fv(withdraw_allow, dec=True))

    add_summary_row(7,
        "Less: Amount Withdrawn till date of this certificate as per the "
        "Books of Accounts and Bank Statement.",
        "", fv(withdrawn_td, dec=True))

    add_summary_row(8,
        "Net Amount which can be Withdrawn from the Designated Bank Account "
        "under this Certificate.",
        "", fv(net_withdraw, dec=True), net=True)

    # ── Signature block 1 ─────────────────────────────────────────
    cert_text = (f"This certificate is being issued for RERA compliance for the Company "
                 f"[{project.get('promoter_name', 'Promoter')}] and is based on the records "
                 f"and documents produced before me and explanations provided to me by the "
                 f"management of the Company.")
    rows.append([cert_text, "", "", ""])
    r = r_idx() - 1
    style_cmds += [('SPAN', (0, r), (3, r)), ('FONTSIZE', (0, r), (3, r), 8)]

    for sig_line in ["Yours Faithfully,",
                     f"Signature of Chartered Accountant – {project.get('ca_name', '')}",
                     f"(Membership No.: {project.get('ca_membership', '…………')})",
                     "______________________", "Name"]:
        rows.append(["", "", sig_line, ""])
        r = r_idx() - 1
        style_cmds += [
            ('SPAN', (2, r), (3, r)),
            ('ALIGN', (2, r), (3, r), 'CENTER'),
            ('FONTSIZE', (0, r), (3, r), 8),
        ]

    # ── Additional Information header ─────────────────────────────
    rows.append(["(ADDITIONAL INFORMATION FOR ONGOING PROJECTS)", "", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (0, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_TITLE),
        ('TEXTCOLOR', (0, r), (3, r), C_WHITE),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 10),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    # ── Additional info rows ──────────────────────────────────────
    def add_addl_row(sr, text, est_val, inc_val):
        r_i = r_idx()
        rows.append([str(sr) if sr is not None else "", text, est_val or "", inc_val or ""])
        style_cmds.extend([
            ('FONTSIZE', (0, r_i), (3, r_i), 8),
            ('ALIGN', (0, r_i), (0, r_i), 'CENTER'),
            ('ALIGN', (2, r_i), (3, r_i), 'RIGHT'),
        ])

    add_addl_row(1,
        "Estimated Balance Cost to Complete the Real Estate Project "
        "(Difference of Total Estimated Project cost less Cost incurred) (calculated as per Form IV)",
        "", fv(bal_cost, dec=True))

    add_addl_row(2,
        "Balance amount of receivables from sold apartments as per Annexure A to this certificate "
        "(as certified by Chartered Accountant as verified from the records and books of Accounts)",
        "", fv(bal_recv_sold, dec=True) if bal_recv_sold else "NIL")

    add_addl_row(3,
        "(i) Balance Unsold area (to be certified by Management and to be verified "
        "by CA from the records and books of accounts)",
        "", f"{unsold_area:,.2f} sq.m." if unsold_area else "NIL")

    add_addl_row(None,
        f"(ii) Estimated amount of sales proceeds in respect of unsold apartments "
        f"(Avg Sale Price per sq.m. of Sold Units: "
        f"Rs.{format_indian_number(int(avg_sale_price)) if avg_sale_price else '—'} × "
        f"Unsold Area: {unsold_area:,.2f} sq.m.) as per Annexure A",
        "", fv(unsold_val, dec=True) if unsold_val else "NIL")

    add_addl_row(4,
        f"Estimated receivables of ongoing project.  "
        f"Total Sale Value of Sold Units (Rs.{format_indian_number(int(total_sale_val_sold)) if total_sale_val_sold else '0'}) + 3(ii)",
        "", fv(total_recv, dec=True) if total_recv else "NIL")

    add_addl_row(5, "Amount to be deposited in Designated Account – 70% or 100%", "", "")

    # 70% / 100% deposit rows
    if total_recv > bal_cost:
        dep_text = (f"IF Sr.4 is GREATER THAN Sr.1: 70% × Rs.{format_indian_number(int(total_recv))} "
                    f"= Rs.{format_indian_number(int(total_recv * 0.70))}")
    else:
        dep_text = (f"IF Sr.4 is LESSER THAN or EQUAL TO Sr.1: 100% × Rs.{format_indian_number(int(total_recv))} "
                    f"= Rs.{format_indian_number(int(total_recv))}")
    r_i = r_idx()
    rows.append(["", dep_text, "", ""])
    style_cmds += [('SPAN', (0, r_i), (3, r_i)), ('FONTSIZE', (0, r_i), (3, r_i), 8),
                   ('FONTNAME', (0, r_i), (3, r_i), 'Helvetica-Bold')]

    # ── Signature block 2 ─────────────────────────────────────────
    rows.append([cert_text, "", "", ""])
    r = r_idx() - 1
    style_cmds += [('SPAN', (0, r), (3, r)), ('FONTSIZE', (0, r), (3, r), 8)]

    for sig_line in ["Yours Faithfully,",
                     "Signature of Chartered Accountant,",
                     f"(Membership No.: {project.get('ca_membership', '…………')})",
                     "______________________", "Name"]:
        rows.append(["", "", sig_line, ""])
        r = r_idx() - 1
        style_cmds += [
            ('SPAN', (2, r), (3, r)),
            ('ALIGN', (2, r), (3, r), 'CENTER'),
            ('FONTSIZE', (0, r), (3, r), 8),
        ]

    # ── Annexure A header ─────────────────────────────────────────
    rows.append(["Annexure A", "", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (0, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_TITLE),
        ('TEXTCOLOR', (0, r), (3, r), C_WHITE),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 12),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    rows.append(["Statement for calculation of Receivables from the Sales of the Ongoing Real Estate Project",
                 "", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (0, r), (3, r)),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    # Sold inventory header
    rows.append(["Sold Inventory", "", "", ""])
    r = r_idx() - 1
    style_cmds += [
        ('SPAN', (0, r), (3, r)),
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 9),
    ]

    # Column headers for Annexure A
    rows.append(["Sr No", "Flat No.", "Received Amount (Rs.)", "Balance Receivable (Rs.)"])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 8),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    sold_sales = [s for s in (sales or []) if s.get("buyer_name")]
    bmap = {b.get("building_id"): b.get("building_name", "") for b in (buildings or [])}
    total_recv_amt = 0; total_bal_recv = 0

    if sold_sales:
        for idx, s in enumerate(sold_sales, 1):
            bname = bmap.get(s.get("building_id"), s.get("building_name", ""))
            unit  = f"{bname} – {s.get('unit_number','')}" if bname else s.get("unit_number", "")
            recv  = s.get("amount_received", 0)
            bal   = s.get("sale_value", 0) - recv
            total_recv_amt += recv; total_bal_recv += bal
            r_i = r_idx()
            rows.append([str(idx), unit, fv(recv, dec=True), fv(bal, dec=True)])
            style_cmds += [('FONTSIZE', (0, r_i), (3, r_i), 8), ('ALIGN', (2, r_i), (3, r_i), 'RIGHT'),
                           ('ALIGN', (0, r_i), (0, r_i), 'CENTER')]
    else:
        for i in range(1, 4):
            r_i = r_idx()
            rows.append([str(i), "", "", ""])
            style_cmds += [('FONTSIZE', (0, r_i), (3, r_i), 8)]

    # Total row
    rows.append(["", "Total", fv(total_recv_amt, dec=True), fv(total_bal_recv, dec=True)])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SUBTOT),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 8),
        ('ALIGN', (2, r), (3, r), 'RIGHT'),
    ]

    # Unsold Inventory valuation box
    unsold_box = (
        f"(Unsold Inventory Valuation)\n"
        f"Average Sale Price per sq.m. of Sold Units: "
        f"Rs. {format_indian_number(int(avg_sale_price)) if avg_sale_price else '—'} per sq.m.\n"
        f"Total Unsold Area: {unsold_area:,.2f} sq.m.\n"
        f"Estimated Unsold Inventory Value (Avg Price × Unsold Area): "
        f"Rs. {format_indian_number(int(unsold_val)) if unsold_val else 'NIL'}"
    )
    rows.append([unsold_box, "", "", ""])
    r = r_idx() - 1
    style_cmds += [('SPAN', (0, r), (3, r)), ('FONTSIZE', (0, r), (3, r), 8)]

    # Unsold unit header
    rows.append(["Sr No", "Flat Number", "Area (sq.m.)", "Estimated Value (Rs.)"])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SECTION),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 8),
        ('ALIGN', (0, r), (3, r), 'CENTER'),
    ]

    unsold_sales = [s for s in (sales or []) if not s.get("buyer_name")]
    total_unsold_area = 0; total_unsold_val = 0
    if unsold_sales:
        for idx, s in enumerate(unsold_sales, 1):
            area = s.get("carpet_area", 0) or 0
            uval = area * avg_sale_price if avg_sale_price else 0
            total_unsold_area += area; total_unsold_val += uval
            bname = bmap.get(s.get("building_id"), s.get("building_name", ""))
            unit  = f"{bname} – {s.get('unit_number','')}" if bname else s.get("unit_number", "")
            r_i = r_idx()
            rows.append([str(idx), unit, f"{area:,.2f}" if area else "", fv(uval, dec=True) if uval else ""])
            style_cmds += [('FONTSIZE', (0, r_i), (3, r_i), 8), ('ALIGN', (2, r_i), (3, r_i), 'RIGHT'),
                           ('ALIGN', (0, r_i), (0, r_i), 'CENTER')]
    else:
        for i in range(1, 4):
            r_i = r_idx()
            rows.append([str(i), "", "", ""])
            style_cmds += [('FONTSIZE', (0, r_i), (3, r_i), 8)]

    # Unsold total row
    rows.append(["", "Total",
                 f"{total_unsold_area:,.2f}" if total_unsold_area else "",
                 fv(total_unsold_val, dec=True) if total_unsold_val else ""])
    r = r_idx() - 1
    style_cmds += [
        ('BACKGROUND', (0, r), (3, r), C_SUBTOT),
        ('FONTNAME', (0, r), (3, r), 'Helvetica-Bold'),
        ('FONTSIZE', (0, r), (3, r), 8),
        ('ALIGN', (2, r), (3, r), 'RIGHT'),
    ]

    # ── Global table style ────────────────────────────────────────
    n_rows = len(rows)
    style_cmds += [
        ('GRID', (0, 0), (-1, -1), 0.4, C_BLACK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]

    main_table = Table(rows, colWidths=CW, repeatRows=4)
    main_table.setStyle(TableStyle(style_cmds))
    elements.append(main_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_annexure_a_pdf(project, sales, buildings, quarter, year):
    """
    ANNEXURE-A: Statement of Receivables from Allottees
    Official Goa RERA Format
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=0.4*inch, bottomMargin=0.4*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    
    # Header
    elements.append(Paragraph("<b>ANNEXURE - A</b>", TITLE_STYLE))
    elements.append(Paragraph("Statement of Receivables from Allottees", SUBTITLE_STYLE))
    elements.append(Spacer(1, 8))
    
    # Project Info
    project_info = f"""<b>Project:</b> {project.get('project_name', '')} | 
    <b>RERA No:</b> {project.get('rera_number', '')} | 
    <b>Quarter:</b> {quarter} {year}
    """
    elements.append(Paragraph(project_info, BODY_STYLE))
    elements.append(Spacer(1, 12))
    
    # Sales Table Headers
    headers = [
        "Sr.", "Unit\nNo.", "Building/\nWing", "Type", "Area\n(sq.m.)", 
        "Agreement\nValue (₹)", "Amount\nReceived (₹)", "Balance\nDue (₹)", 
        "Due\nDate", "Allottee\nName"
    ]
    
    table_data = [headers]
    
    # Build sales data
    building_lookup = {b.get('building_id'): b.get('building_name', '') for b in (buildings or [])}
    
    total_value = 0
    total_received = 0
    total_balance = 0
    
    for idx, sale in enumerate(sales or [], 1):
        agreement_value = sale.get('sale_value', sale.get('agreement_value', 0))
        amount_received = sale.get('amount_received', 0)
        balance = agreement_value - amount_received

        total_value += agreement_value
        total_received += amount_received
        total_balance += balance

        row = [
            str(idx),
            sale.get('unit_number', ''),
            building_lookup.get(sale.get('building_id'), sale.get('building_name', '')),
            sale.get('unit_type', sale.get('flat_type', '')),
            str(sale.get('carpet_area', '')),
            format_indian_number(agreement_value),
            format_indian_number(amount_received),
            format_indian_number(balance),
            format_date(sale.get('agreement_date', sale.get('due_date', ''))),
            sale.get('buyer_name', sale.get('allottee_name', ''))
        ]
        table_data.append(row)
    
    # Add total row
    table_data.append([
        "", "", "", "", "TOTAL",
        format_indian_number(total_value),
        format_indian_number(total_received),
        format_indian_number(total_balance),
        "", ""
    ])
    
    if len(table_data) == 1:
        table_data.append(["", "No sales data available", "", "", "", "", "", "", "", ""])
    
    # Create table
    col_widths = [0.4*inch, 0.6*inch, 0.8*inch, 0.6*inch, 0.6*inch, 
                  1.1*inch, 1.1*inch, 1*inch, 0.8*inch, 1.5*inch]
    
    sales_table = Table(table_data, colWidths=col_widths)
    sales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (5, 1), (7, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(sales_table)
    elements.append(Spacer(1, 20))
    
    # Summary
    summary_text = f"""<b>Summary:</b> Total Units: {len(sales or [])} | 
    Total Agreement Value: ₹{format_indian_number(total_value)} | 
    Total Received: ₹{format_indian_number(total_received)} | 
    Total Balance Due: ₹{format_indian_number(total_balance)}
    """
    elements.append(Paragraph(summary_text, BODY_STYLE))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
