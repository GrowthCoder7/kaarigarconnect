from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import os

os.makedirs("static/demo", exist_ok=True)
output_path = "static/demo/udyam-certificate.pdf"

doc = SimpleDocTemplate(output_path, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

GOV_BLUE   = colors.HexColor("#003580")
GOV_ORANGE = colors.HexColor("#FF6200")
GOV_GREEN  = colors.HexColor("#138808")
LIGHT_BLUE = colors.HexColor("#eaf2ff")

def style(name, **kwargs):
    return ParagraphStyle(name, **kwargs)

story = []
story.append(HRFlowable(width="100%", thickness=6, color=GOV_BLUE, spaceAfter=8))
story.append(Paragraph("Government of India | भारत सरकार", style("s1", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#444"), alignment=TA_CENTER, spaceAfter=2)))
story.append(Paragraph("Ministry of Micro, Small &amp; Medium Enterprises", style("s2", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#444"), alignment=TA_CENTER, spaceAfter=2)))
story.append(Spacer(1, 4))
story.append(Paragraph("UDYAM REGISTRATION CERTIFICATE", style("s3", fontName="Helvetica-Bold", fontSize=13, textColor=GOV_BLUE, alignment=TA_CENTER, spaceAfter=2)))
story.append(HRFlowable(width="100%", thickness=2, color=GOV_ORANGE, spaceAfter=10))

udyam_num = Table([[Paragraph("UDYAM-MP-12-0012345", style("un", fontName="Helvetica-Bold", fontSize=18, textColor=colors.white, alignment=TA_CENTER))]], colWidths=["100%"])
udyam_num.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GOV_BLUE),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
story.append(udyam_num)
story.append(Spacer(1, 14))

fl = style("fl", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#666"))
fv = style("fv", fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#111"))

details = [
    ["Name of Enterprise", "Sunita Handlooms"],
    ["Name of Proprietor", "Sunita Devi"],
    ["Type of Organisation", "Proprietorship"],
    ["Social Category", "General"],
    ["Gender", "Female"],
    ["Date of Registration", "25-05-2025"],
    ["Major Activity", "Manufacturing"],
    ["NIC 5 Digit Code", "13111"],
    ["Activity", "Weaving and finishing of textiles using handloom"],
    ["District", "Chanderi"],
    ["State", "Madhya Pradesh"],
    ["PIN", "473446"],
    ["Persons Employed (Female)", "1"],
    ["Turnover (₹ Lakhs)", "2.00"],
]
table_data = [[Paragraph(l, fl), Paragraph(v, fv)] for l, v in details]
dt = Table(table_data, colWidths=[8.5*cm, 9.5*cm])
dt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(0,-1),LIGHT_BLUE),
    ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#ccc")),
    ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, LIGHT_BLUE]),
]))
story.append(dt)
story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=4, color=GOV_ORANGE, spaceAfter=0))
doc.build(story)
print(f"Certificate generated: {output_path}")