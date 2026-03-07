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
    """Format number as Indian currency"""
    if amount is None:
        return "0"
    return f"₹{amount:,.2f}"

def format_indian_number(num):
    """Format number in Indian numbering system (lakhs, crores)"""
    if num is None:
        return "0"
    return f"{num:,.0f}"

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
    {project.get('promoter_address', project.get('address', '________________________'))},<br/>
    {project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}
    """
    elements.append(Paragraph(to_text, BODY_STYLE))
    elements.append(Spacer(1, 8))
    
    # Date
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", RIGHT_STYLE))
    elements.append(Spacer(1, 10))
    
    # Subject line
    num_buildings = len(buildings) if buildings else "__"
    phase = project.get('phase', '1')
    subject_text = f"""<b>Subject:</b> Certificate of Percentage of Completion of Construction Work of 
    <b>{num_buildings}</b> Building(s) / Wing(s) of the <b>{phase}</b> Phase of the Project situated on the Plot bearing 
    Survey No./Plot No. <b>{project.get('survey_number', '________')}</b> of Ward <b>{project.get('ward', '________')}</b> 
    Municipality <b>{project.get('municipality', '________')}</b> District <b>{project.get('district', 'North Goa')}</b> 
    PIN <b>{project.get('pin_code', '________')}</b> village/panchayat <b>{project.get('village', '________')}</b> 
    taluka <b>{project.get('taluka', '________')}</b> admeasuring <b>{project.get('total_area', '________')}</b> sq.mts. 
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
    admeasuring <b>{project.get('total_area', '________')}</b> sq.mts. area being developed by 
    <b>{project.get('promoter_name', '________')}</b>.
    """
    elements.append(Paragraph(assignment_text, BODY_STYLE))
    elements.append(Spacer(1, 12))
    
    # Technical Professionals Section
    elements.append(Paragraph("<b>1. Following technical professionals are appointed by Owner / Promoter:-</b>", BODY_STYLE))
    elements.append(Spacer(1, 6))
    
    professionals = [
        [f"(i) M/s/Shri/Smt. {project.get('architect_name', '________________________')} as Architect;"],
        [f"(ii) M/s/Shri/Smt. {project.get('structural_consultant', '________________________')} as Structural Consultant;"],
        [f"(iii) M/s/Shri/Smt. {project.get('mep_consultant', '________________________')} as MEP Consultant;"],
        [f"(iv) M/s/Shri/Smt. {project.get('site_supervisor', '________________________')} as Site Supervisor;"],
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


def generate_form3_pdf(project, buildings, building_costs, estimated_dev_cost, quarter, year):
    """
    FORM-3: Engineer's Certificate - Cost Incurred for Development
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
    {project.get('promoter_address', project.get('address', '________________________'))},<br/>
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
    elements.append(Paragraph("<b>TABLE A: Cost Incurred for Building Construction</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    # Get building costs
    building_costs_lookup = {bc.get('building_id'): bc for bc in (building_costs or [])}
    est_cost = estimated_dev_cost or {}
    
    table_a_data = [
        ["Sr.", "Building/Wing", "Estimated Cost (₹)", "Cost Incurred (₹)", "Balance (₹)"]
    ]
    
    total_estimated = 0
    total_incurred = 0
    
    for idx, building in enumerate(buildings or [], 1):
        bc = building_costs_lookup.get(building.get('building_id'), {})
        est = building.get('estimated_cost', 0)
        incurred = bc.get('actual_cost', 0)
        balance = est - incurred
        
        total_estimated += est
        total_incurred += incurred
        
        table_a_data.append([
            str(idx),
            building.get('building_name', ''),
            format_indian_number(est),
            format_indian_number(incurred),
            format_indian_number(balance)
        ])
    
    table_a_data.append([
        "", "TOTAL", format_indian_number(total_estimated), 
        format_indian_number(total_incurred), format_indian_number(total_estimated - total_incurred)
    ])
    
    table_a = Table(table_a_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.3*inch])
    table_a.setStyle(TableStyle([
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table_a)
    elements.append(Spacer(1, 15))
    
    # TABLE B - Development Works Cost
    elements.append(Paragraph("<b>TABLE B: Cost of Internal/External Development Works</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    infra_cost = est_cost.get('infrastructure_cost', 0)
    
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
        ["", "TOTAL INFRASTRUCTURE", format_indian_number(infra_cost), "-", "-"],
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


def generate_form4_pdf(project, project_cost, estimated_dev_cost, quarter, year):
    """
    FORM-4: Chartered Accountant's Certificate - Project Cost Statement
    Official Goa RERA Format
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
    
    elements.append(Paragraph("<b>FORM 4</b>", TITLE_STYLE))
    elements.append(Paragraph("<i>(See Rule 5 (1) (a) (ii))</i>", RULE_STYLE))
    elements.append(Paragraph("<b>CHARTERED ACCOUNTANT'S CERTIFICATE</b>", SUBTITLE_STYLE))
    elements.append(Paragraph("(Project Cost Statement)", SMALL_STYLE))
    elements.append(Spacer(1, 15))
    
    # To section
    to_text = f"""<b>To</b><br/>
    {project.get('promoter_name', '________________________')},<br/>
    {project.get('promoter_address', project.get('address', '________________________'))},<br/>
    {project.get('village', '')}, {project.get('taluka', '')}, {project.get('district', 'Goa')}
    """
    elements.append(Paragraph(to_text, BODY_STYLE))
    elements.append(Spacer(1, 8))
    
    # Date
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", RIGHT_STYLE))
    elements.append(Spacer(1, 10))
    
    # Subject
    subject_text = f"""<b>Subject:</b> Certificate of Project Cost for the Project 
    <b>{project.get('project_name', '________')}</b> registered under GoaRERA.
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
    ca_name = project.get('ca_name', '________________________')
    assignment_text = f"""I/We <b>{ca_name}</b>, Chartered Accountant(s), have examined the books of accounts and 
    records of the promoter and certify the following with respect to the project cost of 
    <b>{project.get('project_name', '________')}</b> as registered under GoaRERA.
    """
    elements.append(Paragraph(assignment_text, BODY_STYLE))
    elements.append(Spacer(1, 15))
    
    # Project Cost Summary Table
    elements.append(Paragraph("<b>PROJECT COST STATEMENT</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    est_cost = estimated_dev_cost or {}
    pc = project_cost or {}
    
    land_cost = est_cost.get('land_cost', 0)
    building_cost = est_cost.get('total_building_cost', 0)
    infra_cost = est_cost.get('infrastructure_cost', 0)
    other_cost = est_cost.get('other_costs', 0)
    total_estimated = land_cost + building_cost + infra_cost + other_cost
    
    cost_data = [
        ["Sr.", "Particulars", "Estimated Cost (₹)", "Actual Cost (₹)"],
        ["1", "Cost of Land", format_indian_number(land_cost), "-"],
        ["2", "Cost of Construction of Buildings", format_indian_number(building_cost), "-"],
        ["3", "Cost of Internal/External Development Works", format_indian_number(infra_cost), "-"],
        ["4", "Administrative and Other Costs", format_indian_number(other_cost), "-"],
        ["", "TOTAL PROJECT COST", format_indian_number(total_estimated), "-"],
    ]
    
    cost_table = Table(cost_data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 1.3*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 20))
    
    # Bank Account Details
    elements.append(Paragraph("<b>DESIGNATED BANK ACCOUNT DETAILS</b>", HEADER_STYLE))
    elements.append(Spacer(1, 8))
    
    bank_data = [
        ["Bank Name:", project.get('bank_name', '________________________')],
        ["Account Number:", project.get('bank_account_number', '________________________')],
        ["IFSC Code:", project.get('bank_ifsc', '________________________')],
        ["Branch:", project.get('bank_branch', '________________________')],
    ]
    
    bank_table = Table(bank_data, colWidths=[1.5*inch, 4*inch])
    bank_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(bank_table)
    elements.append(Spacer(1, 25))
    
    # Closing
    elements.append(Paragraph("<b>Yours Faithfully,</b>", BODY_STYLE))
    elements.append(Spacer(1, 30))
    
    # Signature block
    sig_data = [
        ["_______________________________", ""],
        ["Signature & Name of Chartered Accountant", ""],
        [f"Name: {project.get('ca_name', '________________________')}", ""],
        [f"Membership No.: {project.get('ca_membership', '________________________')}", ""],
        [f"Firm Registration No.: {project.get('ca_firm_reg', '________________________')}", ""],
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
        agreement_value = sale.get('agreement_value', 0)
        amount_received = sale.get('amount_received', 0)
        balance = agreement_value - amount_received
        
        total_value += agreement_value
        total_received += amount_received
        total_balance += balance
        
        row = [
            str(idx),
            sale.get('unit_number', ''),
            building_lookup.get(sale.get('building_id'), sale.get('building_id', '')),
            sale.get('unit_type', ''),
            str(sale.get('carpet_area', '')),
            format_indian_number(agreement_value),
            format_indian_number(amount_received),
            format_indian_number(balance),
            format_date(sale.get('due_date', '')),
            sale.get('allottee_name', '')
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
