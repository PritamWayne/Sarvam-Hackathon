"""
Document Pre-processing Pipeline for Scanned Land Deeds.
Implements Deskewing, Contrast Enhancement, and Margin Notes (Kaifiyat) Isolation.
"""

import os
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional, List
import pypdfium2 as pdfium


class DocumentPreprocessor:
    def __init__(self, output_debug_dir: Optional[str] = "debug_preprocessed"):
        self.output_debug_dir = output_debug_dir
        if self.output_debug_dir and not os.path.exists(self.output_debug_dir):
            os.makedirs(self.output_debug_dir, exist_ok=True)

    def load_document_as_image(self, file_path: str) -> np.ndarray:
        """
        Loads an image or the first page of a PDF as a BGR numpy array.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            pdf = pdfium.PdfDocument(file_path)
            if len(pdf) == 0:
                raise ValueError("PDF document is empty")
            page = pdf[0]
            # Render at 300 DPI for high fidelity
            pil_image = page.render(scale=300 / 72).to_pil()
            img_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return img_bgr
        else:
            img = cv2.imread(file_path)
            if img is None:
                # Try opening with PIL for unicode paths
                pil_img = Image.open(file_path).convert("RGB")
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            return img

    def detect_skew_angle(self, gray: np.ndarray) -> float:
        """
        Calculates skew angle of scanned deed using Hough Lines and MinAreaRect.
        """
        # Invert colors: text as foreground
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15
        )

        # Detect prominent lines with HoughLinesP
        lines = cv2.HoughLinesP(
            thresh, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=20
        )

        angles = []
        if lines is not None:
            for line in lines:
                coords = line.reshape(-1)
                if len(coords) >= 4:
                    x1, y1, x2, y2 = coords[:4]
                    if abs(x2 - x1) > 0.001:
                        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                        # Land deeds are roughly horizontal text; keep small angles
                        if -45 < angle < 45:
                            angles.append(angle)

        if angles:
            # Median angle of detected text/table lines
            median_angle = float(np.median(angles))
            return median_angle

        # Fallback to minAreaRect on non-zero points
        pts = cv2.findNonZero(thresh)
        if pts is not None:
            rect = cv2.minAreaRect(pts)
            angle = rect[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            return float(angle)

        return 0.0

    def deskew(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Rotates the image to compensate for scanner skew while preserving borders.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        skew_angle = self.detect_skew_angle(gray)

        # Skip negligible skew
        if abs(skew_angle) < 0.2:
            return image, 0.0

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, skew_angle, 1.0)

        # Calculate new bounding dimensions to avoid cutting off corners
        cos = np.abs(rot_mat[0, 0])
        sin = np.abs(rot_mat[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        rot_mat[0, 2] += (new_w / 2) - center[0]
        rot_mat[1, 2] += (new_h / 2) - center[1]

        deskewed = cv2.warpAffine(
            image,
            rot_mat,
            (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )
        return deskewed, skew_angle

    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhances contrast, levels illumination, and sharpens faint revenue ink.
        1. Converts to LAB color space.
        2. Applies CLAHE on Lightness (L) channel.
        3. Background normalization to reduce scan shadows/yellowing.
        4. Mild unsharp masking for sharp text strokes.
        """
        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # CLAHE on L channel
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)

        # Background illumination leveling
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        bg_illum = cv2.morphologyEx(l_clahe, cv2.MORPH_CLOSE, kernel)
        norm_l = cv2.divide(l_clahe, bg_illum, scale=255)

        # Merge back
        lab_enhanced = cv2.merge([norm_l, a, b])
        enhanced_bgr = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        # Unsharp mask to crisply define Hindi text and signatures
        gaussian = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.0)
        sharpened = cv2.addWeighted(enhanced_bgr, 1.35, gaussian, -0.35, 0)

        return sharpened

    def isolate_margin_notes(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Segments the document into central body and margins (Kaifiyat / remarks column).
        In Indian revenue records (e.g. Khatauni, Sale Deeds):
        - Left margin (12-18% of width): Frequently records Kaifiyat (remarks, mutations).
        - Right margin (10-15% of width): Stamp duty endorsements, registration folios.
        - Bottom margin (15-20% of height): Tehsildar/Patwari sign-off, date stamps.
        - Center body: Tenure holder table, Khasra numbers, plot areas.
        """
        h, w = image.shape[:2]

        left_margin_w = int(w * 0.16)
        right_margin_w = int(w * 0.14)
        bottom_margin_h = int(h * 0.20)
        top_margin_h = int(h * 0.14)

        # Crop regions
        left_margin_crop = image[top_margin_h : h - bottom_margin_h, 0:left_margin_w]
        right_margin_crop = image[top_margin_h : h - bottom_margin_h, w - right_margin_w : w]
        bottom_margin_crop = image[h - bottom_margin_h : h, :]
        top_header_crop = image[0:top_margin_h, :]
        center_body_crop = image[top_margin_h : h - bottom_margin_h, left_margin_w : w - right_margin_w]

        # Analyze activity in left margin (Kaifiyat)
        gray_left = cv2.cvtColor(left_margin_crop, cv2.COLOR_BGR2GRAY)
        _, thresh_left = cv2.threshold(gray_left, 200, 255, cv2.THRESH_BINARY_INV)
        ink_pixel_ratio_left = float(np.count_nonzero(thresh_left)) / float(thresh_left.size)

        has_marginal_notes = ink_pixel_ratio_left > 0.015

        margin_data = {
            "dimensions": {"width": w, "height": h},
            "left_margin": {
                "bbox": {"x": 0, "y": top_margin_h, "width": left_margin_w, "height": h - top_margin_h - bottom_margin_h},
                "has_notes": bool(has_marginal_notes),
                "ink_density": float(ink_pixel_ratio_left),
                "image": left_margin_crop,
            },
            "right_margin": {
                "bbox": {"x": w - right_margin_w, "y": top_margin_h, "width": right_margin_w, "height": h - top_margin_h - bottom_margin_h},
                "image": right_margin_crop,
            },
            "bottom_margin": {
                "bbox": {"x": 0, "y": h - bottom_margin_h, "width": w, "height": bottom_margin_h},
                "image": bottom_margin_crop,
            },
            "top_header": {
                "bbox": {"x": 0, "y": 0, "width": w, "height": top_margin_h},
                "image": top_header_crop,
            },
            "center_body": {
                "bbox": {"x": left_margin_w, "y": top_margin_h, "width": w - left_margin_w - right_margin_w, "height": h - top_margin_h - bottom_margin_h},
                "image": center_body_crop,
            },
        }

        return margin_data

    def process(self, file_path: str, save_debug: bool = True) -> Dict[str, Any]:
        """
        Runs the full pre-processing pipeline:
        1. Load image/PDF
        2. Deskew
        3. Contrast enhance
        4. Isolate margin notes
        """
        raw_image = self.load_document_as_image(file_path)
        deskewed_image, skew_angle = self.deskew(raw_image)
        enhanced_image = self.enhance_contrast(deskewed_image)
        margin_info = self.isolate_margin_notes(enhanced_image)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        enhanced_path = None

        if save_debug and self.output_debug_dir:
            enhanced_path = os.path.join(self.output_debug_dir, f"{base_name}_enhanced.png")
            cv2.imwrite(enhanced_path, enhanced_image)

            # Save left margin crop for inspection
            left_crop_path = os.path.join(self.output_debug_dir, f"{base_name}_left_margin.png")
            cv2.imwrite(left_crop_path, margin_info["left_margin"]["image"])

        return {
            "raw_image": raw_image,
            "deskewed_image": deskewed_image,
            "enhanced_image": enhanced_image,
            "enhanced_path": enhanced_path,
            "skew_angle": float(skew_angle),
            "margin_info": margin_info,
        }
