"""
Synthetic Land Deed Generator for Testing Ingestion & Verification.
Generates an authentic scanned Indian Land Deed (Khatauni / Revenue Record)
complete with:
- Hindi & English bilingual typography
- Tabular ownership data & Khasra numbers
- Violet/Indigo circular official revenue stamp (मुहर)
- Blue handwritten signatures (हस्ताक्षर - तहसीलदार व पटवारी)
- Marginal Remarks (Kaifiyat / कैफियत) column
- Artificial scanning noise, paper grain, and slight rotation skew to test deskewing.
"""

import os
import math
import random
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


def get_indic_font(size: int = 24):
    """Attempts to find Nirmala UI, Mangal, or Arial for Devanagari text."""
    candidate_paths = [
        "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/mangal.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_scanned_land_deed(output_path: str = "sample_land_deed.png", skew_angle: float = -2.2):
    width, height = 1800, 2400

    # 1. Background paper with slight sepia/cream aged patina
    img = Image.new("RGB", (width, height), color=(250, 248, 240))
    draw = ImageDraw.Draw(img)

    title_font = get_indic_font(42)
    header_font = get_indic_font(28)
    body_font = get_indic_font(24)
    small_font = get_indic_font(18)
    stamp_font = get_indic_font(22)

    # Outer decorative deed border
    draw.rectangle([(30, 30), (width - 30, height - 30)], outline=(60, 50, 40), width=4)
    draw.rectangle([(40, 40), (width - 40, height - 40)], outline=(120, 100, 80), width=1)

    # 2. Government Header (UP Revenue Department / राजस्व परिषद)
    draw.text((width // 2, 80), "उत्तर प्रदेश शासन — राजस्व विभाग", fill=(30, 30, 30), font=title_font, anchor="mm")
    draw.text((width // 2, 135), "अधिकार अभिलेख (खतौनी) — प्रारूप आर.सी.-9", fill=(50, 50, 50), font=header_font, anchor="mm")
    draw.text((width // 2, 175), "(उ०प्र० राजस्व संहिता, 2006 की धारा 31/32 के अधीन)", fill=(80, 80, 80), font=small_font, anchor="mm")

    # Document registration badge
    draw.rectangle([(width - 450, 60), (width - 60, 140)], outline=(100, 100, 100), width=2)
    draw.text((width - 255, 85), "अभिलेख क्रमांक / Deed ID:", fill=(60, 60, 60), font=small_font, anchor="mm")
    draw.text((width - 255, 115), "UP-REV/2024/99201", fill=(10, 10, 10), font=header_font, anchor="mm")

    draw.line([(50, 210), (width - 50, 210)], fill=(80, 70, 60), width=2)

    # 3. Geographic Jurisdiction Section
    info_y = 230
    draw.text((70, info_y), "राज्य: उत्तर प्रदेश (Uttar Pradesh)", fill=(20, 20, 20), font=body_font)
    draw.text((650, info_y), "ज़िला: मेरठ (Meerut)", fill=(20, 20, 20), font=body_font)
    draw.text((1200, info_y), "तहसील: मवाना (Mawana)", fill=(20, 20, 20), font=body_font)

    info_y += 45
    draw.text((70, info_y), "ग्राम/मौज़ा: खासपुर (Khaspur - कोड 11842)", fill=(20, 20, 20), font=body_font)
    draw.text((650, info_y), "परगना: हस्तिनापुर (Hastinapur)", fill=(20, 20, 20), font=body_font)
    draw.text((1200, info_y), "पटवार हल्का: 04", fill=(20, 20, 20), font=body_font)

    info_y += 45
    draw.text((70, info_y), "खाता संख्या (Khata No.): 00184", fill=(10, 10, 10), font=body_font)
    draw.text((650, info_y), "कुल क्षेत्रफल: 3.75 बीघा (0.9485 हेक्टेयर)", fill=(10, 10, 10), font=body_font)
    draw.text((1200, info_y), "दिनांक: 15/10/2024", fill=(20, 20, 20), font=body_font)

    draw.line([(50, info_y + 40), (width - 50, info_y + 40)], fill=(120, 110, 100), width=2)

    # 4. Main Tabular Grid with Marginal Remarks (Kaifiyat) Column
    table_top = info_y + 60
    table_bottom = 1750
    left_margin_x = 380  # Column 1: Kaifiyat (0 to 380)

    # Column coordinates
    col_x = [60, 380, 820, 1120, 1340, 1540, width - 60]

    # Draw table outer border
    draw.rectangle([(col_x[0], table_top), (col_x[-1], table_bottom)], outline=(40, 40, 40), width=3)

    # Column lines
    for cx in col_x[1:-1]:
        draw.line([(cx, table_top), (cx, table_bottom)], fill=(80, 80, 80), width=2)

    # Header Row
    header_h = 90
    draw.rectangle([(col_x[0], table_top), (col_x[-1], table_top + header_h)], fill=(240, 235, 220), outline=(40, 40, 40), width=2)

    headers = [
        "1. कैफियत / टिप्पणी\n(Marginal Remarks)",
        "2. खातेदारों के नाम व पिता का नाम\n(Tenure Holders)",
        "3. खसरा / गाटा संख्या\n(Khasra Numbers)",
        "4. अंश (Share)\nFraction",
        "5. प्रतिशत\nShare %",
        "6. आबंटित क्षेत्रफल\nAllocated Area",
    ]

    for i in range(len(headers)):
        c_left = col_x[i]
        c_right = col_x[i + 1]
        c_mid = (c_left + c_right) // 2
        draw.text((c_mid, table_top + 45), headers[i], fill=(20, 20, 20), font=small_font, anchor="mm", align="center")

    # Table Data Rows
    row1_y = table_top + header_h + 30
    draw.text((col_x[1] + 15, row1_y), "सुरेश कुमार (Suresh Kumar)", fill=(10, 10, 10), font=body_font)
    draw.text((col_x[1] + 15, row1_y + 35), "आत्मज: स्व० रामस्वरूप शर्मा", fill=(70, 70, 70), font=small_font)
    draw.text((col_x[1] + 15, row1_y + 60), "निवास: ग्राम खासपुर, मवाना", fill=(90, 90, 90), font=small_font)

    draw.text(((col_x[2] + col_x[3]) // 2, row1_y + 30), "154/1, 154/2\n(2.50 बीघा)", fill=(10, 10, 10), font=body_font, anchor="mm", align="center")
    draw.text(((col_x[3] + col_x[4]) // 2, row1_y + 30), "1/2", fill=(10, 10, 10), font=body_font, anchor="mm")
    draw.text(((col_x[4] + col_x[5]) // 2, row1_y + 30), "50.00%", fill=(10, 10, 10), font=body_font, anchor="mm")
    draw.text(((col_x[5] + col_x[6]) // 2, row1_y + 30), "1.875 बीघा", fill=(10, 10, 10), font=body_font, anchor="mm")

    draw.line([(col_x[1], row1_y + 110), (col_x[-1], row1_y + 110)], fill=(150, 150, 150), width=1)

    row2_y = row1_y + 140
    draw.text((col_x[1] + 15, row2_y), "महेश कुमार (Mahesh Kumar)", fill=(10, 10, 10), font=body_font)
    draw.text((col_x[1] + 15, row2_y + 35), "आत्मज: स्व० रामस्वरूप शर्मा", fill=(70, 70, 70), font=small_font)
    draw.text((col_x[1] + 15, row2_y + 60), "निवास: ग्राम खासपुर, मवाना", fill=(90, 90, 90), font=small_font)

    draw.text(((col_x[2] + col_x[3]) // 2, row2_y + 30), "156\n(1.25 बीघा)", fill=(10, 10, 10), font=body_font, anchor="mm", align="center")
    draw.text(((col_x[3] + col_x[4]) // 2, row2_y + 30), "1/2", fill=(10, 10, 10), font=body_font, anchor="mm")
    draw.text(((col_x[4] + col_x[5]) // 2, row2_y + 30), "50.00%", fill=(10, 10, 10), font=body_font, anchor="mm")
    draw.text(((col_x[5] + col_x[6]) // 2, row2_y + 30), "1.875 बीघा", fill=(10, 10, 10), font=body_font, anchor="mm")

    # Draw Marginal Remarks (Kaifiyat / कैफियत) in Column 1
    kaifiyat_text = (
        "आदेश न्यायालय तहसीलदार मवाना:\n"
        "वाद सं० 1042/2024 अंतर्गत धारा 34\n"
        "उ०प्र० रा० संहिता।\n\n"
        "दिनांक 12/09/2024 को बैनामा सं०\n"
        "4321/2024 के आधार पर स्व०\n"
        "रामस्वरूप के स्थान पर वारिसान\n"
        "सुरेश व महेश कुमार के नाम\n"
        "दाखिल खारिज (Mutation) आदेश\n"
        "स्वीकार हुआ।\n\n"
        "कोई बंधक / बैंक ऋण शेष नहीं।"
    )
    draw.text((col_x[0] + 15, table_top + header_h + 20), kaifiyat_text, fill=(40, 40, 80), font=small_font)

    # 5. Attestation & Signatures Section (Bottom area)
    sig_section_y = 1840
    draw.line([(50, sig_section_y), (width - 50, sig_section_y)], fill=(80, 80, 80), width=2)
    draw.text((width // 2, sig_section_y + 25), "प्रमाणीकरण एवं सत्यापन (Attestation & Verification)", fill=(40, 40, 40), font=header_font, anchor="mm")

    draw.text((150, sig_section_y + 90), "हस्ताक्षर पटवारी / लेखपाल", fill=(30, 30, 30), font=body_font)
    draw.text((150, sig_section_y + 125), "हल्का पटवारी: रामपाल सिंह", fill=(80, 80, 80), font=small_font)

    draw.text((width - 450, sig_section_y + 90), "हस्ताक्षर तहसीलदार / राजस्व अधिकारी", fill=(30, 30, 30), font=body_font)
    draw.text((width - 450, sig_section_y + 125), "तहसीलदार: वी० के० सक्सेना", fill=(80, 80, 80), font=small_font)

    # Convert PIL Image to OpenCV for stamp & signature drawing and scan-artifact synthesis
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # 6. Draw Official Revenue Seal / Stamp (मुहर) in Violet / Indigo Ink
    # Positioned at (width - 550, 1920)
    stamp_center = (width - 320, 2090)
    stamp_radius = 85
    stamp_color = (138, 43, 120)  # Violet BGR: (Blue=138, Green=43, Red=120)

    # Outer double ring
    cv2.circle(img_cv, stamp_center, stamp_radius, stamp_color, 4, cv2.LINE_AA)
    cv2.circle(img_cv, stamp_center, stamp_radius - 12, stamp_color, 2, cv2.LINE_AA)
    cv2.circle(img_cv, stamp_center, 6, stamp_color, -1, cv2.LINE_AA)

    # Stamp text
    cv2.putText(img_cv, "* NYAYALAYA TEHSILDAR *", (stamp_center[0] - 78, stamp_center[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.40, stamp_color, 1, cv2.LINE_AA)
    cv2.putText(img_cv, "MAWANA (MEERUT)", (stamp_center[0] - 65, stamp_center[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, stamp_color, 2, cv2.LINE_AA)
    cv2.putText(img_cv, "UTTAR PRADESH", (stamp_center[0] - 58, stamp_center[1] + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.40, stamp_color, 1, cv2.LINE_AA)
    cv2.putText(img_cv, "15 OCT 2024", (stamp_center[0] - 45, stamp_center[1] + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.45, stamp_color, 2, cv2.LINE_AA)

    # 7. Draw Realistic Handwritten Signatures in Blue Pen Ink
    # Tehsildar signature (cursive stroke loops)
    sig_tehsildar_color = (160, 45, 20)  # Dark Blue BGR
    pts_t = np.array([
        [width - 430, 2010], [width - 400, 1985], [width - 370, 2025],
        [width - 340, 1970], [width - 310, 2015], [width - 270, 1980],
        [width - 230, 2020], [width - 180, 1975], [width - 140, 2010]
    ], np.int32)
    cv2.polylines(img_cv, [pts_t], False, sig_tehsildar_color, 3, cv2.LINE_AA)
    cv2.ellipse(img_cv, (width - 300, 1995), (65, 30), 20, 0, 360, sig_tehsildar_color, 2, cv2.LINE_AA)
    cv2.line(img_cv, (width - 450, 2030), (width - 120, 2020), sig_tehsildar_color, 2, cv2.LINE_AA)

    # Patwari signature
    sig_patwari_color = (180, 50, 30)  # Blue BGR
    pts_p = np.array([
        [160, 2015], [190, 1980], [220, 2020],
        [250, 1975], [290, 2010], [330, 1985],
        [370, 2025], [410, 1990]
    ], np.int32)
    cv2.polylines(img_cv, [pts_p], False, sig_patwari_color, 3, cv2.LINE_AA)
    cv2.ellipse(img_cv, (280, 1995), (55, 25), -15, 0, 360, sig_patwari_color, 2, cv2.LINE_AA)
    cv2.line(img_cv, (140, 2035), (430, 2025), sig_patwari_color, 2, cv2.LINE_AA)

    # 8. Add realistic scanning skew (-2.2 degrees) and scanner dust/paper grain
    if abs(skew_angle) > 0.1:
        h, w = img_cv.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
        img_cv = cv2.warpAffine(img_cv, rot_mat, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

    # Add subtle scanner noise
    noise = np.random.normal(0, 3, img_cv.shape).astype(np.float32)
    img_cv = np.clip(img_cv.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # Save generated deed
    cv2.imwrite(output_path, img_cv)
    print(f"Sample Scanned Land Deed created successfully at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_scanned_land_deed()
