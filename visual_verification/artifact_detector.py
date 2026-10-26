"""
Visual Authenticity Markers Detector for Scanned Indian Land Deeds.
Detects:
1. Official Revenue / Judicial Ink Stamps (मुहर) & Headers
2. Tehsildar / Patwari / Revenue Officer Signatures (हस्ताक्षर)
3. Marginal Remarks (Kaifiyat / कैफियत)
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from models.deed_schema import VisualArtifact, VisualVerificationReport, BoundingBox


class VisualArtifactDetector:
    def __init__(self, debug_dir: Optional[str] = "debug_visual_artifacts"):
        self.debug_dir = debug_dir
        if self.debug_dir and not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir, exist_ok=True)

    def detect_revenue_stamps(self, image: np.ndarray) -> List[VisualArtifact]:
        """
        Detects official revenue stamps, circular seals (मुहर), and stamp paper headers.
        Uses HSV color thresholding (violet, blue, red stamp ink) and contour circularity / Hough circles.
        """
        h, w = image.shape[:2]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        detected_stamps: List[VisualArtifact] = []

        # 1. Official Purple/Violet ink mask (Standard Indian Revenue Seal ink)
        # H: 125-165, S: 45-255, V: 40-245
        lower_violet = np.array([125, 40, 40])
        upper_violet = np.array([165, 255, 245])
        violet_mask = cv2.inRange(hsv, lower_violet, upper_violet)

        # 2. Official Crimson/Red ink mask
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        red_mask = cv2.bitwise_or(
            cv2.inRange(hsv, lower_red1, upper_red1),
            cv2.inRange(hsv, lower_red2, upper_red2),
        )

        # 3. Official Blue ink mask
        lower_blue = np.array([95, 60, 40])
        upper_blue = np.array([124, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Combined stamp ink mask
        stamp_ink_mask = cv2.bitwise_or(violet_mask, red_mask)
        stamp_ink_mask = cv2.bitwise_or(stamp_ink_mask, blue_mask)

        # Morphological closing to join seal characters and rings
        kernel_seal = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        closed_mask = cv2.morphologyEx(stamp_ink_mask, cv2.MORPH_CLOSE, kernel_seal, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(closed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        stamp_idx = 1
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter by area: stamps in 300DPI scans are typically 2,000 to 120,000 px
            if area < 1500 or area > (h * w * 0.25):
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = float(bw) / float(bh) if bh > 0 else 0

            # Round / oval stamps have aspect ratio close to 1.0 (0.65 to 1.5)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))

            # Sample ink color inside contour
            mask_crop = stamp_ink_mask[y : y + bh, x : x + bw]
            v_count = np.count_nonzero(violet_mask[y : y + bh, x : x + bw])
            r_count = np.count_nonzero(red_mask[y : y + bh, x : x + bw])
            b_count = np.count_nonzero(blue_mask[y : y + bh, x : x + bw])

            dominant_ink = "violet_purple"
            if r_count > v_count and r_count > b_count:
                dominant_ink = "red_crimson"
            elif b_count > v_count and b_count > r_count:
                dominant_ink = "blue_indigo"

            # Check if this qualifies as an official revenue seal
            if (circularity > 0.35 and 0.65 <= aspect_ratio <= 1.55) or (area > 5000 and 0.5 <= aspect_ratio <= 2.0):
                confidence = min(0.98, float(0.65 + (circularity * 0.25) + (min(area, 20000) / 20000 * 0.1)))
                detected_stamps.append(
                    VisualArtifact(
                        id=f"stamp_{stamp_idx}",
                        type="revenue_stamp",
                        bounding_box=BoundingBox(x=int(x), y=int(y), width=int(bw), height=int(bh)),
                        confidence=round(confidence, 2),
                        label="Official Revenue Seal / Stamp (मुहर)",
                        details={
                            "ink_profile": dominant_ink,
                            "circularity": round(float(circularity), 3),
                            "contour_area_px": int(area),
                            "aspect_ratio": round(float(aspect_ratio), 2),
                        },
                    )
                )
                stamp_idx += 1

        # Fallback to Hough Circle transform if no contour stamp was captured
        if not detected_stamps:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.medianBlur(gray, 5)
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1.2,
                minDist=100,
                param1=100,
                param2=45,
                minRadius=30,
                maxRadius=120,
            )
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for c in circles[0, :]:
                    cx, cy, cr = c
                    bx = max(0, int(cx - cr))
                    by = max(0, int(cy - cr))
                    bw = min(w - bx, int(cr * 2))
                    bh = min(h - by, int(cr * 2))
                    detected_stamps.append(
                        VisualArtifact(
                            id=f"stamp_hough_{stamp_idx}",
                            type="revenue_stamp",
                            bounding_box=BoundingBox(x=bx, y=by, width=bw, height=bh),
                            confidence=0.78,
                            label="Circular Official Seal Impression (मुहर)",
                            details={"method": "hough_circle", "radius_px": int(cr)},
                        )
                    )
                    stamp_idx += 1

        # Check top header for Non-Judicial Stamp Paper banner (Ashoka emblem / value banner)
        top_banner_h = int(h * 0.15)
        top_banner = image[0:top_banner_h, :]
        gray_banner = cv2.cvtColor(top_banner, cv2.COLOR_BGR2GRAY)
        edge_density = float(np.count_nonzero(cv2.Canny(gray_banner, 80, 180))) / float(gray_banner.size)
        if edge_density > 0.05:
            detected_stamps.append(
                VisualArtifact(
                    id="stamp_paper_header",
                    type="stamp_paper_header",
                    bounding_box=BoundingBox(x=0, y=0, width=w, height=top_banner_h),
                    confidence=0.88,
                    label="Official Revenue Stamp Paper Header (ई-स्टाम्प / भारत सरकार)",
                    details={"edge_density": round(edge_density, 3)},
                )
            )

        return detected_stamps

    def detect_signatures(
        self, image: np.ndarray, margin_info: Optional[Dict[str, Any]] = None
    ) -> List[VisualArtifact]:
        """
        Detects handwritten signatures of Tehsildar, Patwari, Sub-Registrar, or parties.
        Uses dual-path detection:
        1. Colored ink stroke analysis (Blue/Cyan pen ink common in Indian revenue offices).
        2. Cursive stroke structural analysis (removing straight table lines, detecting handwriting loops).
        """
        h, w = image.shape[:2]
        bottom_zone_y = int(h * 0.70)
        signature_candidates: List[VisualArtifact] = []

        # -------------------------------------------------------------------------
        # Path A: Blue / Pen Ink Signature Detection
        # -------------------------------------------------------------------------
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([90, 25, 25])
        upper_blue = np.array([135, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Connect cursive pen strokes
        kernel_blue = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 6))
        dilated_blue = cv2.dilate(blue_mask, kernel_blue, iterations=2)

        contours_blue, _ = cv2.findContours(dilated_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        sig_idx = 1
        for cnt in contours_blue:
            x, y, bw, bh = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            # Legitimate handwritten signatures in 300 DPI land deeds:
            # - Width: 100 - 550 px, Height: 30 - 180 px
            # - Located in lower 30% of page or margin zones
            if bw < 100 or bh < 30 or bw > 600 or bh > 220:
                continue

            in_bottom_zone = (y + bh) >= bottom_zone_y
            in_margin_zone = (x < int(w * 0.18)) or ((x + bw) > int(w * 0.82))

            if not (in_bottom_zone or in_margin_zone):
                continue

            aspect_ratio = float(bw) / float(bh)
            if aspect_ratio < 1.1 or aspect_ratio > 8.0:
                continue

            # Role attribution
            role_label = "Official Signature (हस्ताक्षर)"
            if in_bottom_zone and (x + bw // 2) > (w * 0.50):
                role_label = "Tehsildar / Revenue Officer Signature (ह० तहसीलदार)"
            elif in_bottom_zone and (x + bw // 2) <= (w * 0.50):
                role_label = "Patwari / Lekhpal Signature (ह० लेखपाल/पटवारी)"
            elif in_margin_zone:
                role_label = "Attestation Signature (हस्ताक्षर तस्दीक)"

            confidence = min(0.96, float(0.78 + (min(bw, 300) / 300 * 0.12) + (0.05 if in_bottom_zone else 0.0)))

            signature_candidates.append(
                VisualArtifact(
                    id=f"signature_{sig_idx}",
                    type="signature",
                    bounding_box=BoundingBox(x=int(x), y=int(y), width=int(bw), height=int(bh)),
                    confidence=round(confidence, 2),
                    label=role_label,
                    details={
                        "detection_path": "blue_pen_ink",
                        "aspect_ratio": round(float(aspect_ratio), 2),
                        "zone": "bottom_zone" if in_bottom_zone else "margin_zone",
                    },
                )
            )
            sig_idx += 1

        # -------------------------------------------------------------------------
        # Path B: Structural Cursive Stroke Detection (for Black ink signatures)
        # -------------------------------------------------------------------------
        if len(signature_candidates) < 2:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10
            )

            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 1))
            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))
            table_lines = cv2.bitwise_or(
                cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel),
                cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel),
            )
            strokes_only = cv2.subtract(binary, table_lines)
            kernel_sig = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 4))
            dilated_strokes = cv2.dilate(strokes_only, kernel_sig, iterations=2)

            cnts_b, _ = cv2.findContours(dilated_strokes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in cnts_b:
                x, y, bw, bh = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)
                if bw < 110 or bh < 35 or bw > 600 or bh > 220:
                    continue
                if (y + bh) < bottom_zone_y:
                    continue
                aspect_ratio = float(bw) / float(bh)
                if 1.2 <= aspect_ratio <= 7.0 and area > 1800:
                    role_label = (
                        "Tehsildar / Revenue Officer Signature (ह० तहसीलदार)"
                        if (x + bw // 2) > (w * 0.50)
                        else "Patwari / Lekhpal Signature (ह० लेखपाल/पटवारी)"
                    )
                    signature_candidates.append(
                        VisualArtifact(
                            id=f"signature_{sig_idx}",
                            type="signature",
                            bounding_box=BoundingBox(x=int(x), y=int(y), width=int(bw), height=int(bh)),
                            confidence=0.84,
                            label=role_label,
                            details={"detection_path": "cursive_strokes", "aspect_ratio": round(aspect_ratio, 2)},
                        )
                    )
                    sig_idx += 1

        merged = self._merge_overlapping_boxes(signature_candidates)
        return merged

        # Non-maximum suppression / merging nearby signature fragments
        merged_signatures = self._merge_overlapping_boxes(signature_candidates)
        return merged_signatures

    def detect_marginal_remarks(
        self, image: np.ndarray, margin_info: Optional[Dict[str, Any]] = None
    ) -> List[VisualArtifact]:
        """
        Detects Kaifiyat (कैफियत) marginal remarks column and annotations.
        """
        h, w = image.shape[:2]
        remarks: List[VisualArtifact] = []

        if margin_info and "left_margin" in margin_info:
            left_info = margin_info["left_margin"]
            if left_info.get("has_notes", False):
                bbox = left_info["bbox"]
                remarks.append(
                    VisualArtifact(
                        id="kaifiyat_left_margin",
                        type="marginal_remark",
                        bounding_box=BoundingBox(
                            x=bbox["x"], y=bbox["y"], width=bbox["width"], height=bbox["height"]
                        ),
                        confidence=0.92,
                        label="Marginal Remarks / Kaifiyat Column (कैफियत स्तम्भ)",
                        details={
                            "ink_density": left_info.get("ink_density", 0.0),
                            "location": "left_column",
                            "has_content": True,
                        },
                    )
                )
        else:
            # Direct margin analysis
            left_w = int(w * 0.16)
            left_crop = image[int(h * 0.15) : int(h * 0.80), 0:left_w]
            gray_crop = cv2.cvtColor(left_crop, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_crop, 200, 255, cv2.THRESH_BINARY_INV)
            density = float(np.count_nonzero(thresh)) / float(thresh.size)
            if density > 0.015:
                remarks.append(
                    VisualArtifact(
                        id="kaifiyat_margin",
                        type="marginal_remark",
                        bounding_box=BoundingBox(x=0, y=int(h * 0.15), width=left_w, height=int(h * 0.65)),
                        confidence=0.88,
                        label="Marginal Remarks (कैफियत)",
                        details={"ink_density": round(density, 3)},
                    )
                )

        return remarks

    def verify_document(
        self, image: np.ndarray, margin_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[VisualVerificationReport, np.ndarray]:
        """
        Runs comprehensive visual verification:
        1. Detects revenue stamps
        2. Detects signatures
        3. Analyzes Kaifiyat remarks
        4. Calculates authenticity scores and creates visual verification overlay image.
        """
        stamps = self.detect_revenue_stamps(image)
        signatures = self.detect_signatures(image, margin_info)
        kaifiyat = self.detect_marginal_remarks(image, margin_info)

        mandatory_stamps_present = len(stamps) > 0
        signatures_present = len(signatures) > 0
        kaifiyat_present = len(kaifiyat) > 0

        # Calculate authenticity score
        score = 0.0
        if mandatory_stamps_present:
            score += 0.45
        if signatures_present:
            score += 0.40
        if kaifiyat_present:
            score += 0.15

        if mandatory_stamps_present and signatures_present:
            authenticity_status = "VERIFIED"
        elif mandatory_stamps_present or signatures_present:
            authenticity_status = "FLAGGED_MISSING_MARKERS"
        else:
            authenticity_status = "INCOMPLETE"

        report = VisualVerificationReport(
            mandatory_stamps_present=mandatory_stamps_present,
            signatures_present=signatures_present,
            kaifiyat_present=kaifiyat_present,
            authenticity_status=authenticity_status,
            authenticity_score=round(score, 2),
            revenue_stamps=stamps,
            signatures=signatures,
            marginal_remarks=kaifiyat,
        )

        # Draw annotated visual verification overlay
        annotated_image = self.draw_verification_overlay(image, stamps, signatures, kaifiyat)

        return report, annotated_image

    def draw_verification_overlay(
        self,
        image: np.ndarray,
        stamps: List[VisualArtifact],
        signatures: List[VisualArtifact],
        kaifiyat: List[VisualArtifact],
    ) -> np.ndarray:
        """
        Draws colored bounding boxes and badges on document:
        - Emerald Green: Official Revenue Stamps & Seals
        - Royal Blue: Signatures (Tehsildar/Patwari)
        - Amber / Orange: Marginal Remarks (Kaifiyat)
        """
        overlay = image.copy()

        # 1. Stamps (Emerald Green: BGR = 34, 139, 34)
        for stamp in stamps:
            bb = stamp.bounding_box
            cv2.rectangle(overlay, (bb.x, bb.y), (bb.x + bb.width, bb.y + bb.height), (34, 180, 34), 3)
            label = f"[STAMP] {stamp.label} ({int(stamp.confidence*100)}%)"
            cv2.putText(
                overlay,
                label,
                (bb.x, max(20, bb.y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (20, 140, 20),
                2,
                cv2.LINE_AA,
            )

        # 2. Signatures (Royal Blue: BGR = 210, 80, 20)
        for sig in signatures:
            bb = sig.bounding_box
            cv2.rectangle(overlay, (bb.x, bb.y), (bb.x + bb.width, bb.y + bb.height), (210, 80, 20), 3)
            label = f"[SIGNATURE] {sig.label} ({int(sig.confidence*100)}%)"
            cv2.putText(
                overlay,
                label,
                (bb.x, max(20, bb.y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (180, 60, 10),
                2,
                cv2.LINE_AA,
            )

        # 3. Kaifiyat (Amber: BGR = 0, 140, 255)
        for k in kaifiyat:
            bb = k.bounding_box
            cv2.rectangle(overlay, (bb.x, bb.y), (bb.x + bb.width, bb.y + bb.height), (0, 140, 255), 3)
            label = f"[KAIFIYAT] {k.label}"
            cv2.putText(
                overlay,
                label,
                (bb.x, max(25, bb.y + 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 120, 220),
                2,
                cv2.LINE_AA,
            )

        return overlay

    def _merge_overlapping_boxes(self, artifacts: List[VisualArtifact]) -> List[VisualArtifact]:
        """
        Merges redundant bounding boxes that heavily overlap.
        """
        if not artifacts:
            return []

        cleaned: List[VisualArtifact] = []
        for a in artifacts:
            keep = True
            for c in cleaned:
                # Calculate Intersection over Union
                ax1, ay1, ax2, ay2 = a.bounding_box.x, a.bounding_box.y, a.bounding_box.x + a.bounding_box.width, a.bounding_box.y + a.bounding_box.height
                cx1, cy1, cx2, cy2 = c.bounding_box.x, c.bounding_box.y, c.bounding_box.x + c.bounding_box.width, c.bounding_box.y + c.bounding_box.height

                inter_x1 = max(ax1, cx1)
                inter_y1 = max(ay1, cy1)
                inter_x2 = min(ax2, cx2)
                inter_y2 = min(ay2, cy2)

                if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                    area_a = a.bounding_box.width * a.bounding_box.height
                    if float(inter_area) / float(area_a) > 0.65:
                        keep = False
                        break
            if keep:
                cleaned.append(a)

        return cleaned
