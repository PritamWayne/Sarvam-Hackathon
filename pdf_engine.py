"""
Court-Ready Legal PDF Engine (ReportLab)
Assembles a complete, downloadable, ready-to-sign legal objection petition under
Section 34/35 of the State Land Revenue Act / U.P. Revenue Code, 2006 before the Tehsildar / SDM,
complete with reconstructed Vanshavali family tree, forensic discrepancy tables, and indexed evidence annexures.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from objection_petition_generator import LegalObjectionDraft
from evidence_indexer import EvidenceDocket, EvidenceExhibit


# Register Indic TrueType font if present for high-fidelity bilingual output
INDIC_FONT_NAME = "Helvetica"
INDIC_BOLD_FONT = "Helvetica-Bold"

try:
    if os.path.exists("C:/Windows/Fonts/Nirmala.ttc"):
        pdfmetrics.registerFont(TTFont("NirmalaUI", "C:/Windows/Fonts/Nirmala.ttc", subfontIndex=0))
        INDIC_FONT_NAME = "NirmalaUI"
        INDIC_BOLD_FONT = "NirmalaUI"
    elif os.path.exists("C:/Windows/Fonts/arial.ttf"):
        pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
        INDIC_FONT_NAME = "Arial"
        INDIC_BOLD_FONT = "Arial-Bold"
except Exception:
    pass


class CourtNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to compute total page numbers and render professional court running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_court_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_court_decorations(self, page_count):
        self.saveState()
        page_w, page_h = A4

        # Margins: 54 pt (0.75 in)
        left_m = 54
        right_m = page_w - 54

        # Top Running Header (Pages 2+)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1A365D"))  # Court Navy
            self.drawString(left_m, page_h - 36, "IN THE COURT OF THE TEHSILDAR / SUB-DIVISIONAL OFFICER, MAWANA (DISTRICT MEERUT)")
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(colors.HexColor("#4A5568"))
            self.drawRightString(right_m, page_h - 36, "CASE NO. 142-M / 2026")

            # Header thin rule
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.6)
            self.line(left_m, page_h - 42, right_m, page_h - 42)

        # Bottom Running Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.6)
        self.line(left_m, 44, right_m, 44)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawString(
            left_m,
            32,
            "PETITION UNDER SEC. 34/35 U.P. REVENUE CODE — HARISHANKAR MISHRA & ORS. VS. KAMLESH MISHRA"
        )

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 8)
        self.drawRightString(right_m, 32, page_str)

        self.restoreState()


class CourtPDFEngine:
    """
    Renders high-grade court-ready legal objection petition PDFs.
    """

    def __init__(self, output_pdf_path: str):
        self.output_pdf_path = Path(output_pdf_path)
        self.output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        self.styles = self._setup_styles()

    def _setup_styles(self) -> Dict[str, ParagraphStyle]:
        base_styles = getSampleStyleSheet()

        styles = {
            "CourtHeading": ParagraphStyle(
                "CourtHeading",
                parent=base_styles["Heading1"],
                fontName=INDIC_BOLD_FONT,
                fontSize=11,
                leading=15,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#1A202C"),
                spaceAfter=4,
                textTransform="uppercase"
            ),
            "CourtSubHeading": ParagraphStyle(
                "CourtSubHeading",
                parent=base_styles["Normal"],
                fontName=INDIC_BOLD_FONT,
                fontSize=9.5,
                leading=13,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#2D3748"),
                spaceAfter=8
            ),
            "CaseBanner": ParagraphStyle(
                "CaseBanner",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=14,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#1A365D"),
                spaceAfter=10
            ),
            "PartyTitle": ParagraphStyle(
                "PartyTitle",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#1A202C")
            ),
            "PartyDetail": ParagraphStyle(
                "PartyDetail",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=11.5,
                textColor=colors.HexColor("#2D3748")
            ),
            "PetitionSubject": ParagraphStyle(
                "PetitionSubject",
                parent=base_styles["Normal"],
                fontName=INDIC_BOLD_FONT,
                fontSize=9.5,
                leading=13.5,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor("#742A2A"),  # Maroon Legal Emphasis
                spaceBefore=6,
                spaceAfter=8
            ),
            "LegalPara": ParagraphStyle(
                "LegalPara",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12.5,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor("#2D3748"),
                spaceAfter=6,
                firstLineIndent=16
            ),
            "LegalParaBold": ParagraphStyle(
                "LegalParaBold",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=12.5,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor("#1A202C"),
                spaceAfter=3
            ),
            "PrayerPara": ParagraphStyle(
                "PrayerPara",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor("#1A202C"),
                spaceAfter=4,
                leftIndent=12
            ),
            "SectionHeader": ParagraphStyle(
                "SectionHeader",
                parent=base_styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#1A365D"),
                spaceBefore=10,
                spaceAfter=4
            ),
            "TableText": ParagraphStyle(
                "TableText",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=8,
                leading=10.5,
                textColor=colors.HexColor("#2D3748")
            ),
            "TableTextBold": ParagraphStyle(
                "TableTextBold",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10.5,
                textColor=colors.HexColor("#1A202C")
            ),
            "TableTextHeader": ParagraphStyle(
                "TableTextHeader",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10.5,
                alignment=TA_CENTER,
                textColor=colors.white
            ),
            "AnnexureStamp": ParagraphStyle(
                "AnnexureStamp",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=15,
                alignment=TA_RIGHT,
                textColor=colors.HexColor("#9B2C2C"),
                spaceAfter=6
            ),
            "SignatureBlock": ParagraphStyle(
                "SignatureBlock",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=11.5,
                alignment=TA_RIGHT,
                textColor=colors.HexColor("#1A202C")
            )
        }
        return styles

    def generate_court_petition_pdf(
        self,
        draft: LegalObjectionDraft,
        docket: EvidenceDocket
    ) -> str:
        """
        Builds and writes the complete multi-page court objection petition PDF.
        """
        doc = SimpleDocTemplate(
            str(self.output_pdf_path),
            pagesize=A4,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        story = []

        # -------------------------------------------------------------
        # PAGE 1: COURT HEADER, PARTIES & CAUSE TITLE
        # -------------------------------------------------------------
        story.append(Paragraph(draft.court_name, self.styles["CourtHeading"]))
        story.append(Paragraph(draft.jurisdiction_title, self.styles["CourtSubHeading"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceAfter=6))
        story.append(Paragraph(f"<b>{draft.case_number}</b>", self.styles["CaseBanner"]))

        # Memo of Parties Table
        parties_data = []

        # Objectors row
        obj_text = "<b>IN THE MATTER OF OBJECTORS / PETITIONERS:</b><br/>"
        for idx, obj in enumerate(draft.objectors, 1):
            obj_text += f"<b>{idx}. {obj.name}</b>, age {obj.age} yrs, s/o {obj.parentage}<br/>&nbsp;&nbsp;&nbsp;&nbsp;r/o {obj.residence} [{obj.role}]<br/>"
        obj_text += "<br/><b>... OBJECTORS / AGGRIEVED CO-SHARERS</b>"

        # Respondents row
        resp_text = "<b>VERSUS RESPONDENTS:</b><br/>"
        for idx, resp in enumerate(draft.respondents, 1):
            if resp.age > 0:
                resp_text += f"<b>{idx}. {resp.name}</b>, age {resp.age} yrs, s/o {resp.parentage}<br/>&nbsp;&nbsp;&nbsp;&nbsp;r/o {resp.residence} [{resp.role}]<br/>"
            else:
                resp_text += f"<b>{idx}. {resp.name}</b> [{resp.role}]<br/>&nbsp;&nbsp;&nbsp;&nbsp;{resp.parentage}, {resp.residence}<br/>"
        resp_text += "<br/><b>... RESPONDENTS / ADVERSE PARTIES</b>"

        parties_table = Table(
            [[Paragraph(obj_text, self.styles["PartyDetail"])],
             [Paragraph("<b>— VERSUS —</b>", ParagraphStyle("Versus", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER, spaceBefore=3, spaceAfter=3))],
             [Paragraph(resp_text, self.styles["PartyDetail"])]],
            colWidths=[doc.width]
        )
        parties_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 8))

        # Subject / Title of Petition
        story.append(Paragraph(f"<b><u>PETITION TITLE & CAUSE OF ACTION:</u></b><br/>{draft.statutory_provisions}", self.styles["PetitionSubject"]))
        story.append(Spacer(1, 4))

        # Subject Land Parcel Details Box
        land_summary_html = (
            f"<b>SUBJECT REVENUE DETAILS:</b> Mauza: <b>{draft.land_info.mauza_village}</b> | Pargana: <b>{draft.land_info.pargana}</b> | "
            f"Tehsil: <b>{draft.land_info.tehsil}</b> | District: <b>{draft.land_info.district}</b><br/>"
            f"• Khata No.: <b>{draft.land_info.khata_number}</b> | Disputed Khasra Nos.: <b>{draft.land_info.khasra_numbers}</b> (Area: <b>{draft.land_info.disputed_parcel_area}</b>)<br/>"
            f"• Total Ancestral Holding: <b>{draft.land_info.total_ancestral_area}</b> | Lawful Share of Objectors' Branch: <b>{draft.land_info.claimant_entitled_area}</b><br/>"
            f"• Unlawful Surplus Mutated to Respondent No. 1: <b><font color='#9B2C2C'>{draft.land_info.unlawful_surplus_area}</font></b>"
        )
        land_box = Table([[Paragraph(land_summary_html, self.styles["TableText"])]], colWidths=[doc.width])
        land_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF5F5")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FEB2B2")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(land_box)
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # INDEX OF PLEADINGS & ANNEXURES
        # -------------------------------------------------------------
        story.append(Paragraph("<b>INDEX OF PLEADINGS & EVIDENCE ANNEXURES</b>", self.styles["SectionHeader"]))
        index_table_data = [
            [Paragraph("<b>Sl. No.</b>", self.styles["TableTextHeader"]),
             Paragraph("<b>Description of Pleading / Document</b>", self.styles["TableTextHeader"]),
             Paragraph("<b>Annexure / Exhibit</b>", self.styles["TableTextHeader"]),
             Paragraph("<b>Page Ref</b>", self.styles["TableTextHeader"])]
        ]

        index_table_data.append([
            Paragraph("1", self.styles["TableText"]),
            Paragraph("Objection Petition under Section 34 & 35 U.P. Revenue Code, 2006", self.styles["TableTextBold"]),
            Paragraph("Main Petition", self.styles["TableTextBold"]),
            Paragraph("Pages 1 - 3", self.styles["TableText"])
        ])
        index_table_data.append([
            Paragraph("2", self.styles["TableText"]),
            Paragraph("Verification Clause & Sworn Supporting Affidavit of Objector No. 1", self.styles["TableText"]),
            Paragraph("Affidavit", self.styles["TableText"]),
            Paragraph("Page 3", self.styles["TableText"])
        ])

        for idx, ex in enumerate(docket.exhibits, 3):
            index_table_data.append([
                Paragraph(str(idx), self.styles["TableText"]),
                Paragraph(f"{ex.title} <i>({ex.issuing_source})</i>", self.styles["TableText"]),
                Paragraph(f"<b>{ex.exhibit_id}</b>", self.styles["TableTextBold"]),
                Paragraph(ex.pages_span, self.styles["TableText"])
            ])

        index_table = Table(index_table_data, colWidths=[36, 260, 110, 80])
        index_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ]))
        story.append(index_table)
        story.append(Spacer(1, 10))

        # -------------------------------------------------------------
        # PRELIMINARY OBJECTIONS
        # -------------------------------------------------------------
        story.append(Paragraph("<b>I. PRELIMINARY OBJECTIONS ON MAINTAINABILITY & FRAUD:</b>", self.styles["SectionHeader"]))
        for po in draft.preliminary_objections:
            story.append(Paragraph(f"• <b>{po}</b>", self.styles["LegalPara"]))
        story.append(Spacer(1, 6))

        # -------------------------------------------------------------
        # STATEMENT OF FACTS
        # -------------------------------------------------------------
        story.append(Paragraph("<b>II. STATEMENT OF MATERIAL FACTS:</b>", self.styles["SectionHeader"]))
        for idx, fact in enumerate(draft.statement_of_facts, 1):
            fact_lead = f"<b>{idx}. {fact['title']}:</b> "
            story.append(Paragraph(fact_lead + fact["text"], self.styles["LegalPara"]))
        story.append(Spacer(1, 6))

        # -------------------------------------------------------------
        # GROUNDS OF OBJECTION
        # -------------------------------------------------------------
        story.append(Paragraph("<b>III. GROUNDS OF OBJECTION & STATUTORY AUTHORITIES:</b>", self.styles["SectionHeader"]))
        for idx, ground in enumerate(draft.legal_grounds, 1):
            ground_head = f"<b>Ground {chr(64 + idx)} — {ground['heading']}:</b> "
            story.append(Paragraph(ground_head + ground["argument"], self.styles["LegalPara"]))
        story.append(Spacer(1, 6))

        # Statutory citations
        citations_text = "<b>Relevant Authorities & Precedents Cited:</b> " + " | ".join(draft.statutory_citations)
        story.append(Paragraph(citations_text, self.styles["LegalParaBold"]))
        story.append(Spacer(1, 8))

        # -------------------------------------------------------------
        # PRAYER CLAUSE
        # -------------------------------------------------------------
        story.append(Paragraph("<b>IV. PRAYER / RELIEFS SOUGHT:</b>", self.styles["SectionHeader"]))
        story.append(Paragraph(
            "WHEREFORE, in light of the foregoing facts, statutory grounds, and overwhelming documentary evidence, "
            "the Objectors most respectfully pray that this Hon'ble Court may be graciously pleased to:—",
            self.styles["LegalParaBold"]
        ))

        prayer_letters = ["(a)", "(b)", "(c)", "(d)", "(e)"]
        for idx, prayer in enumerate(draft.prayers):
            letter = prayer_letters[idx] if idx < len(prayer_letters) else f"({idx+1})"
            story.append(Paragraph(f"<b>{letter}</b> {prayer}", self.styles["PrayerPara"]))

        story.append(Spacer(1, 8))
        story.append(Paragraph("AND / OR pass such other and further orders as this Hon'ble Court may deem fit and proper in the interests of justice.", self.styles["LegalParaBold"]))
        story.append(Spacer(1, 12))

        # -------------------------------------------------------------
        # SIGNATURES & VERIFICATION
        # -------------------------------------------------------------
        sig_data = [
            [
                Paragraph("<b>COUNSEL FOR OBJECTORS</b><br/>Advocate, Civil Court & Tehsil Bar<br/>Mawana / Meerut", self.styles["PartyTitle"]),
                Paragraph("<b>OBJECTORS / PETITIONERS:</b><br/>"
                          "1. ________________________ (Harishankar Mishra)<br/>"
                          "2. ________________________ (Umashankar Mishra)<br/>"
                          "3. ________________________ (Ravishankar Mishra)<br/>"
                          f"Dated: {draft.date_of_filing}", self.styles["SignatureBlock"])
            ]
        ]
        sig_table = Table(sig_data, colWidths=[240, 246])
        sig_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_table)
        story.append(Spacer(1, 10))

        # Verification Box
        story.append(Paragraph("<b><u>VERIFICATION</u></b>", ParagraphStyle("VerHead", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER)))
        story.append(Paragraph(draft.verification_text, self.styles["LegalPara"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>DEPONENTS / OBJECTORS</b>", ParagraphStyle("Dep", fontName="Helvetica-Bold", fontSize=8.5, alignment=TA_RIGHT)))
        story.append(Spacer(1, 8))

        # Supporting Affidavit
        story.append(Paragraph("<b><u>SUPPORTING AFFIDAVIT</u></b>", ParagraphStyle("AffHead", fontName="Helvetica-Bold", fontSize=9, alignment=TA_CENTER)))
        for para in draft.affidavit_text.split("\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles["LegalPara"]))
        story.append(Paragraph("<b>DEPONENT (Harishankar Mishra)</b>", ParagraphStyle("Dep2", fontName="Helvetica-Bold", fontSize=8.5, alignment=TA_RIGHT)))

        # -------------------------------------------------------------
        # PAGE BREAK FOR EVIDENCE ANNEXURES
        # -------------------------------------------------------------
        for ex in docket.exhibits:
            story.append(PageBreak())
            story.append(Paragraph(f"<b>{ex.exhibit_id}</b>", self.styles["AnnexureStamp"]))
            story.append(Paragraph(f"<b><u>{ex.title.upper()}</u></b>", self.styles["CourtHeading"]))
            story.append(Paragraph(f"<b>Source Authority:</b> {ex.issuing_source} | <b>Date/Period:</b> {ex.date_or_period}", self.styles["CourtSubHeading"]))
            story.append(Paragraph(f"<b>Legal Evidentiary Relevance:</b> {ex.legal_relevance}", self.styles["PetitionSubject"]))
            story.append(Spacer(1, 6))

            # Special rendering for Vanshavali Visual Hierarchy Tree
            if ex.exhibit_id == "ANNEXURE P-1":
                vanshavali_tree_table = self._build_visual_vanshavali_tree()
                story.append(vanshavali_tree_table)
                story.append(Spacer(1, 8))

            # Render Annexure Structured Table
            if ex.table_headers and ex.table_rows:
                annex_table_data = [
                    [Paragraph(f"<b>{h}</b>", self.styles["TableTextHeader"]) for h in ex.table_headers]
                ]
                for r in ex.table_rows:
                    row_cells = []
                    for c_idx, cell_val in enumerate(r):
                        # Color coding for Surplus / Deficit Alerts in Annexure P-3
                        if "SURPLUS" in str(cell_val):
                            p_style = ParagraphStyle("SurplusCell", parent=self.styles["TableTextBold"], textColor=colors.HexColor("#C53030"))
                        elif "DEFICIT" in str(cell_val):
                            p_style = ParagraphStyle("DeficitCell", parent=self.styles["TableTextBold"], textColor=colors.HexColor("#DD6B20"))
                        elif c_idx == 0:
                            p_style = self.styles["TableTextBold"]
                        else:
                            p_style = self.styles["TableText"]
                        row_cells.append(Paragraph(str(cell_val), p_style))
                    annex_table_data.append(row_cells)

                # Adjust column widths dynamically based on number of columns
                num_cols = len(ex.table_headers)
                col_w = doc.width / num_cols
                col_widths = [col_w] * num_cols
                if num_cols == 6:
                    col_widths = [50, 110, 80, 80, 75, 91]
                elif num_cols == 5:
                    col_widths = [90, 115, 95, 75, 111]
                elif num_cols == 3:
                    col_widths = [110, 240, 136]

                annex_table = Table(annex_table_data, colWidths=col_widths)
                annex_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                ]))
                story.append(annex_table)
                story.append(Spacer(1, 10))

            # Attestation Stamp at foot of each annexure
            attest_box = Table(
                [[Paragraph("<b>TRUE EXTRACT & ATTESTED EXHIBIT</b><br/>Filed on behalf of Objectors by Counsel", self.styles["TableTextBold"]),
                  Paragraph("<b>Sd/-</b><br/>Harishankar Mishra (Objector No. 1)<br/>Identified by Counsel", self.styles["SignatureBlock"])]],
                colWidths=[240, 246]
            )
            attest_box.setStyle(TableStyle([
                ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#A0AEC0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(Spacer(1, 10))
            story.append(attest_box)

        # Build document
        doc.build(story, canvasmaker=CourtNumberedCanvas)
        return str(self.output_pdf_path.resolve())

    def _build_visual_vanshavali_tree(self) -> Table:
        """
        Creates a structured visual pedigree flowchart table representing the Vanshavali tree.
        """
        styles = self.styles

        root_cell = Paragraph(
            "<para align='center'><b>COMMON ANCESTOR (KARTA): RAMESHWAR MISHRA</b><br/>"
            "<i>(Demised: 1984 | Total Ancestral Holding: 12 Bigha 0 Biswa = 100%)</i></para>",
            styles["TableTextBold"]
        )

        arrow_cell = Paragraph("<para align='center'><b>│<br/>├────────────────────────────────────────┴────────────────────────────────────────┤</b></para>", styles["TableText"])

        branch_a_cell = Paragraph(
            "<para align='center'><b>BRANCH A (50% = 6 Bigha)</b><br/>"
            "<b>Late Bholanath Mishra</b><br/>"
            "<i>(Eldest Son | Demised: 2008)</i><br/>"
            "<b>1988 Chakbandi Allottee</b></para>",
            styles["TableTextBold"]
        )

        branch_b_cell = Paragraph(
            "<para align='center'><b>BRANCH B (50% = 6 Bigha)</b><br/>"
            "<b>Late Dinanath Mishra</b><br/>"
            "<i>(Younger Son | Demised: 2019)</i><br/>"
            "<b>1988 Chakbandi Allottee</b></para>",
            styles["TableTextBold"]
        )

        heir_a_cell = Paragraph(
            "<b>Heirs of Bholanath Mishra (Objectors):</b><br/>"
            "• <b>Harishankar Mishra</b> (Objector 1): <b>2 Bigha (16.67%)</b><br/>"
            "• <b>Umashankar Mishra</b> (Objector 2): <b>2 Bigha (16.67%)</b><br/>"
            "• <b>Ravishankar Mishra</b> (Objector 3): <b>2 Bigha (16.67%)</b><br/>"
            "<font color='#C53030'><b>STATUS: Unlawfully deprived of 4 Bighas in Khasra 142 & 143</b></font>",
            styles["TableText"]
        )

        heir_b_cell = Paragraph(
            "<b>Sole Heir of Dinanath Mishra (Respondent):</b><br/>"
            "• <b>Kamlesh Mishra</b> (Respondent 1): <b>6 Bigha (50%)</b><br/>"
            "<font color='#9B2C2C'><b>IMPUGNED MUTATION: Recorded over 10 Bighas</b></font><br/>"
            "<font color='#C53030'><b>FORENSIC FINDING: +4 Bigha Unlawful Surplus Grab</b></font>",
            styles["TableText"]
        )

        tree_data = [
            [root_cell, ""],
            [arrow_cell, ""],
            [branch_a_cell, branch_b_cell],
            [heir_a_cell, heir_b_cell]
        ]

        tree_table = Table(tree_data, colWidths=[243, 243])
        tree_table.setStyle(TableStyle([
            ("SPAN", (0, 0), (1, 0)),
            ("SPAN", (0, 1), (1, 1)),
            ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#EBF8FF")),
            ("BOX", (0, 0), (1, 0), 1, colors.HexColor("#3182CE")),
            ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#F0FFF4")),
            ("BOX", (0, 2), (0, 2), 1, colors.HexColor("#38A169")),
            ("BACKGROUND", (1, 2), (1, 2), colors.HexColor("#FFF5F5")),
            ("BOX", (1, 2), (1, 2), 1, colors.HexColor("#E53E3E")),
            ("BACKGROUND", (0, 3), (0, 3), colors.HexColor("#F7FAFC")),
            ("BOX", (0, 3), (0, 3), 0.5, colors.HexColor("#CBD5E0")),
            ("BACKGROUND", (1, 3), (1, 3), colors.HexColor("#FFF5F5")),
            ("BOX", (1, 3), (1, 3), 0.5, colors.HexColor("#FEB2B2")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return tree_table
