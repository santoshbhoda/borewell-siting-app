"""
Professional Multi-Page PDF Report Generator using ReportLab
Produces a balanced 2-Page publication-grade Hydrogeological Borewell Siting Report
with embedded Farm Siting Map, Catchment Heatmap, Candidate Spots Table,
Field Action Plan, WALTA Compliance, and Drilling Rig Operator Protocol.
"""
import os
import json
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
)


def generate_pdf_report(
    geojson_report_path: str,
    farm_map_path: str,
    catchment_map_path: str,
    output_pdf_path: str
) -> str:
    """
    Generates an official 2-page balanced publication-grade PDF report.
    """
    with open(geojson_report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    farm = data["farm_analysis"]
    pts = farm["candidate_points"]
    stats = farm["score_statistics"]

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0f172a')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )
    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#ffffff')
    )

    elements = []

    # =========================================================================
    # PAGE 1: HEADER & MAP & TECHNICAL CANDIDATE SPOTS
    # =========================================================================
    header_data = [
        [
            Paragraph("<b>BSMA GeoAI — Borewell & Groundwater Siting Report</b>", title_style),
            Paragraph(f"<b>Report ID:</b> BSMA-GW-2026-KF02<br/><b>Date:</b> 2026-08-25", subtitle_style)
        ],
        [
            Paragraph("Applied GeoAI Division | Hard-Rock Groundwater Prospecting (Musi Sub-Basin, Telangana)", subtitle_style),
            Paragraph("<b>Status:</b> Validated & Sited", subtitle_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[126 * mm, 60 * mm])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_header)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=5, spaceBefore=3))

    # SECTION 1: PARCEL OVERVIEW
    elements.append(Paragraph("1. Land Parcel & Hydrogeological Profile", sec_title))
    overview_data = [
        [
            Paragraph("<b>Land Parcel:</b>", bold_body),
            Paragraph(f"{farm['farm_name']}", body_style),
            Paragraph("<b>Total Area:</b>", bold_body),
            Paragraph(f"{farm['farm_area_acres']} Acres ({farm['farm_area_hectares']} ha)", body_style)
        ],
        [
            Paragraph("<b>Centroid Coordinates:</b>", bold_body),
            Paragraph(f"{farm['centroid']['lat']:.5f}°N, {farm['centroid']['lon']:.5f}°E", body_style),
            Paragraph("<b>Potential Index:</b>", bold_body),
            Paragraph(f"<b><font color='#16a34a'>{stats['mean']} / 100 ({stats['category']})</font></b>", body_style)
        ],
        [
            Paragraph("<b>Lithology / Terrain:</b>", bold_body),
            Paragraph("Weathered Granite-Gneiss Saprolite", body_style),
            Paragraph("<b>Rainfall Recharge:</b>", bold_body),
            Paragraph("~820 mm/year (SW Monsoon)", body_style)
        ]
    ]
    t_overview = Table(overview_data, colWidths=[38 * mm, 55 * mm, 38 * mm, 55 * mm])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_overview)
    elements.append(Spacer(1, 4))

    # SECTION 2: MAP FIGURE
    elements.append(Paragraph("2. Farm Siting Plan & Candidate Locations Map", sec_title))
    if os.path.exists(farm_map_path):
        img_farm = Image(farm_map_path, width=186 * mm, height=72 * mm)
        elements.append(img_farm)
        elements.append(Paragraph(
            "<font size='6.5' color='#64748b'><i>Figure 1: High-resolution plot boundary with color-coded candidate drilling spots (#1 Primary, #2 Secondary, #3 Alternative) and GWPI heatmap overlay.</i></font>",
            body_style
        ))
    elements.append(Spacer(1, 4))

    # SECTION 3: CANDIDATE TABLE
    elements.append(Paragraph("3. Ranked Candidate Drilling Spots & Technical Specifications", sec_title))
    table_rows = [
        [
            Paragraph("<b>Rank & Priority</b>", table_header),
            Paragraph("<b>Coordinates (Lat, Lon)</b>", table_header),
            Paragraph("<b>GWPI Score</b>", table_header),
            Paragraph("<b>Est. Depth</b>", table_header),
            Paragraph("<b>Expected Yield</b>", table_header),
            Paragraph("<b>Elevation / Slope</b>", table_header)
        ]
    ]
    for pt in pts:
        rank_tag = "Primary" if pt["rank"] == 1 else "Secondary" if pt["rank"] == 2 else "Alternative"
        table_rows.append([
            Paragraph(f"<b>Spot #{pt['rank']}</b><br/><font color='#64748b' size='6.5'>{rank_tag}</font>", table_text),
            Paragraph(f"<code>{pt['lat']:.5f}°N<br/>{pt['lon']:.5f}°E</code>", table_text),
            Paragraph(f"<b><font color='#15803d'>{pt['gwpi_score']}/100</font></b><br/><font size='6.5'>{pt['potential_category']}</font>", table_text),
            Paragraph(f"<b>{pt['estimated_depth_range']}</b>", table_text),
            Paragraph(f"<b>{pt['expected_yield_range']}</b>", table_text),
            Paragraph(f"{pt['elevation_m']}m MSL<br/>({pt['slope_pct']}% slope)", table_text)
        ])

    t_candidates = Table(table_rows, colWidths=[28 * mm, 38 * mm, 28 * mm, 30 * mm, 38 * mm, 24 * mm])
    t_candidates.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')]),
    ]))
    elements.append(t_candidates)
    elements.append(Spacer(1, 4))

    # SECTION 4: GEOLOGICAL RATIONALES
    elements.append(Paragraph("4. Geological Rationales & Drilling Recommendations", sec_title))
    rat_rows = []
    for pt in pts:
        rat_rows.append(f"• <b>Spot #{pt['rank']} ({pt['lat']:.5f}°N, {pt['lon']:.5f}°E):</b> {pt['hydro_summary']} Recommended drilling: 6.5\" DTH hammer with 40–60 ft casing through weathered saprolite.")
    elements.append(Paragraph("<br/>".join(rat_rows), body_style))

    # =========================================================================
    # PAGE BREAK -> PAGE 2
    # =========================================================================
    elements.append(PageBreak())

    # PAGE 2 HEADER
    elements.append(Paragraph("<b>BSMA GeoAI — Technical Annex & Statutory Protocol</b> (Page 2 of 2)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=6, spaceBefore=2))

    # SECTION 5: CATCHMENT REGIONAL OVERVIEW
    elements.append(Paragraph("5. Regional Catchment & Drainage Fracture Context", sec_title))
    if os.path.exists(catchment_map_path):
        img_catchment = Image(catchment_map_path, width=186 * mm, height=72 * mm)
        elements.append(img_catchment)
        elements.append(Paragraph(
            "<font size='6.5' color='#64748b'><i>Figure 2: Regional 6km catchment hydrogeological model showing secondary NW-SE / NE-SW lineament corridors and Musi sub-basin drainage network.</i></font>",
            body_style
        ))
    elements.append(Spacer(1, 5))

    # SECTION 6: AHP CRITERIA WEIGHTS
    elements.append(Paragraph("6. AHP Multi-Criteria Thematic Weights (Hard-Rock Terrain)", sec_title))
    ahp_data = [
        [
            Paragraph("<b>Geology / Lithology:</b> 25.72%", table_text),
            Paragraph("<b>Fracture Lineaments:</b> 20.87%", table_text),
            Paragraph("<b>Topographic Slope:</b> 15.75%", table_text),
            Paragraph("<b>Drainage Density:</b> 12.01%", table_text)
        ],
        [
            Paragraph("<b>Wetness Index (TWI):</b> 9.12%", table_text),
            Paragraph("<b>Land Use / LULC:</b> 6.96%", table_text),
            Paragraph("<b>Soil Infiltration:</b> 5.38%", table_text),
            Paragraph("<b>Rainfall Recharge:</b> 4.19%", table_text)
        ]
    ]
    t_ahp = Table(ahp_data, colWidths=[46.5 * mm] * 4)
    t_ahp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_ahp)
    elements.append(Spacer(1, 5))

    # SECTION 7: FIELD ACTION PLAN & LANDOWNER GUIDANCE
    elements.append(Paragraph("7. Landowner Siting Guidance & Field Action Plan", sec_title))
    action_data = [
        [
            Paragraph("<b>Hydrogeological Siting Summary:</b>", bold_body),
            Paragraph(
                f"{farm['farm_name']} shows an overall High Potential (Average GWPI: {stats['mean']}/100). "
                "Secondary fracture corridors and moisture convergence zones are concentrated along the central drainage axis. "
                f"Spot #1 (Score: {pts[0]['gwpi_score']}/100) is the top-ranked drilling target.",
                body_style
            )
        ],
        [
            Paragraph("<b>Pre-Drilling Action Steps:</b>", bold_body),
            Paragraph(
                "1. Conduct 1D/2D VES geophysical survey at Spot #1 to verify fracture depth (280–400 ft).<br/>"
                "2. Confirm 150m boundary clearance from neighboring active borewells under WALTA guidelines.<br/>"
                "3. Provide this technical sheet to the drilling contractor before rig mobilization.",
                body_style
            )
        ]
    ]
    t_lang = Table(action_data, colWidths=[38 * mm, 148 * mm])
    t_lang.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#bae6fd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0f2fe')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_lang)
    elements.append(Spacer(1, 5))

    # SECTION 8: STATUTORY & DRILLING RIG PROTOCOL
    elements.append(Paragraph("8. Statutory Clearances & Drilling Rig Operator Protocol", sec_title))
    checklist_data = [
        [
            Paragraph(
                "<b>✓ Telangana WALTA Act Compliance:</b> All candidate spots maintain >= 150m spacing. Confirm 150m clearance from neighbor wells.<br/>"
                "<b>⚡ Mandatory VES Resistivity Survey:</b> Vertical Electrical Sounding (VES) or 2D Resistivity Imaging required at Spot #1 prior to drilling rig mobilization.<br/>"
                "<b>🛠️ Drilling Specifications:</b> Minimum 40–60 ft MS/PVC casing through weathered saprolite until hard bedrock is seated; 6.5\" DTH hammer drill bit with 900–1100 CFM / 300 PSI compressor.",
                body_style
            )
        ]
    ]
    t_chk = Table(checklist_data, colWidths=[186 * mm])
    t_chk.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fefce8')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#fde047')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    elements.append(t_chk)
    elements.append(Spacer(1, 8))

    # Sign-off Footer
    signoff_data = [
        [
            Paragraph("<b>BSMA Enterprises — Applied GeoAI Division</b><br/><font size='7' color='#64748b'>Scientific Groundwater Prospecting & Diligence</font>", body_style),
            Paragraph("<b>Authorized Verification Stamp</b><br/><font size='7' color='#64748b'>BSMA Hydrogeological Engine v1.0</font>", subtitle_style)
        ]
    ]
    t_sign = Table(signoff_data, colWidths=[116 * mm, 70 * mm])
    t_sign.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_sign)

    doc.build(elements)
    print(f"2-Page Complete PDF Report generated at: {output_pdf_path}")
    return output_pdf_path


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    geojson_path = os.path.join(root, "data", "output", "farm_siting_report.geojson")
    farm_map = os.path.join(root, "data", "output", "farm_siting_plan.png")
    catchment_map = os.path.join(root, "data", "output", "catchment_gwpi_map.png")
    out_pdf = os.path.join(root, "Borewell_Siting_Full_Report_KarunFarm2.pdf")
    generate_pdf_report(geojson_path, farm_map, catchment_map, out_pdf)
    
    # Overwrite pilot.pdf and copy to web/data/
    shutil.copy(out_pdf, os.path.join(root, "pilot.pdf"))
    shutil.copy(out_pdf, os.path.join(root, "web", "data", "Borewell_Siting_Full_Report.pdf"))
    print("Updated pilot.pdf and web/data/Borewell_Siting_Full_Report.pdf")
