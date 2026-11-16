"""Generate professional PDF reports with ReportLab."""
import os
from datetime import datetime
from typing import Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

FONT = None
for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]:
    if os.path.exists(fp):
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont("DejaVu", fp))
            FONT = "DejaVu"
            break
        except Exception:
            pass
FONT = FONT or "Helvetica"

def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="CTitle", fontName=FONT, fontSize=22, alignment=1, spaceAfter=20, textColor=HexColor("#1a1a2e")))
    s.add(ParagraphStyle(name="CHead", fontName=FONT, fontSize=14, spaceBefore=12, textColor=HexColor("#16213e")))
    s.add(ParagraphStyle(name="CBody", fontName=FONT, fontSize=10, leading=14, spaceBefore=4))
    s.add(ParagraphStyle(name="CCaption", fontName=FONT, fontSize=8, alignment=1, textColor=HexColor("#666666")))
    return s

def create_report_pdf(
    title, output_path, study_area="", objective="",
    data_sources=None, methods=None, results_text="",
    map_images=None, tables=None, author="NEXORA AI Team",
):
    data_sources = data_sources or []
    methods = methods or []
    map_images = map_images or []
    tables = tables or []
    try:
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                 rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        styles = _styles()
        story = []

        story.append(Spacer(1, 3*cm))
        story.append(Paragraph(title, styles["CTitle"]))
        story.append(Spacer(1, 0.5*cm))
        if study_area:
            story.append(Paragraph("<b>Wilayah Kajian:</b> " + study_area, styles["CBody"]))
        story.append(Paragraph("<b>Tanggal:</b> " + datetime.now().strftime("%d %B %Y"), styles["CBody"]))
        story.append(Paragraph("<b>Pembuat:</b> " + author, styles["CBody"]))
        story.append(Spacer(1, 1*cm))

        if objective:
            story.append(Paragraph("Tujuan Analisis", styles["CHead"]))
            story.append(Paragraph(objective, styles["CBody"]))
            story.append(Spacer(1, 0.5*cm))

        if data_sources:
            story.append(Paragraph("Sumber Data", styles["CHead"]))
            for src in data_sources:
                story.append(Paragraph("• " + src, styles["CBody"]))
            story.append(Spacer(1, 0.5*cm))

        if methods:
            story.append(Paragraph("Metodologi", styles["CHead"]))
            for m in methods:
                story.append(Paragraph(m, styles["CBody"]))
            story.append(Spacer(1, 0.5*cm))

        if results_text:
            story.append(Paragraph("Hasil Analisis", styles["CHead"]))
            story.append(Paragraph(results_text, styles["CBody"]))
            story.append(Spacer(1, 0.5*cm))

        for img_path in map_images:
            if os.path.exists(img_path):
                try:
                    im = Image(img_path, width=15*cm, height=10*cm)
                    story.append(im)
                    story.append(Paragraph("Gambar: " + os.path.basename(img_path), styles["CCaption"]))
                    story.append(Spacer(1, 0.3*cm))
                except Exception:
                    pass

        doc.build(story)
        size_kb = os.path.getsize(output_path) / 1024 if os.path.exists(output_path) else 0
        return {"success": True, "output_path": output_path, "size_kb": round(size_kb, 1)}
    except Exception as e:
        return {"success": False, "error": str(e)}
