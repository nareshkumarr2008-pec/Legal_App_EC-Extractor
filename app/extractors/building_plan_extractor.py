# -*- coding: utf-8 -*-
"""
Dedicated Approved Building Plan (கட்டிட அனுமதி வரைபடம்) Extractor.
Authoritatively extracts planning permits, building use (Commercial / Residential / Mixed Use),
sanctioning authority details, survey boundaries, and built-up areas.
"""

import re
from typing import Dict, Any


class BuildingPlanExtractor:
    """Extractor for Approved Building Plan documents."""

    def __init__(self):
        pass

    def _find_value(self, text: str, patterns, flags=re.IGNORECASE):
        for pat in patterns:
            m = re.search(pat, text, flags)
            if m:
                res = m.group(1).strip()
                res = re.sub(r'^[=:\-\s|]+|[=:\-\s|]+$', '', res).strip()
                if res:
                    return res
        return None

    def _detect_building_use(self, text: str) -> str:
        """Detect building occupancy (Commercial / Residential / Mixed Use / Industrial)."""
        text_lower = text.lower()

        # 1. Commercial / Office / Shop
        if any(k in text_lower for k in [
            "commercial", "retail", "shopping", "office", "வணிகக் கடை",
            "வணிக வளாகம்", "கடை", "வணிகம்", "shop no", "hotel", "restaurant", "உணவகம்"
        ]):
            return "Commercial — Shop / Office / Commercial Establishment (வணிக பயன்பாடு)"

        # 2. Mixed use
        if any(k in text_lower for k in ["mixed use", "residential cum commercial", "கலப்பு பயன்பாடு"]):
            return "Mixed Use — Commercial & Residential (கலப்பு வணிகம் & குடியிருப்பு)"

        # 3. Residential
        if any(k in text_lower for k in ["residential", "dwelling", "வீடு", "குடியிருப்பு", "மனை"]):
            return "Residential — House / Apartment (குடியிருப்பு)"

        # 4. Industrial
        if any(k in text_lower for k in ["industrial", "factory", "தொழிற்சாலை", "தொழிலகம்"]):
            return "Industrial — Factory / Warehouse (தொழிற்சாலை)"

        return "Commercial / General Occupancy (வணிகம் / பொது பயன்பாடு)"

    def _detect_shop_details(self, text: str) -> str:
        """Detect shop/unit code or number if explicitly stated in text."""
        m_shop = re.search(
            r'(?:shop\s*(?:no|code|number)|கடை\s*எண்|stall\s*(?:no|code)|unit\s*(?:no|code))[:\s\.\-]+([A-Za-z0-9\-\/]+(?:\s+[A-Za-z0-9\-\/]+)?)',
            text,
            re.IGNORECASE
        )
        if m_shop:
            return f"Unit / Shop No: {m_shop.group(1).strip()}"

        return "Not Specified (-)"

    def extract(self, text: str) -> Dict[str, Any]:
        fields = {}

        # 1. Primary Building Use
        building_use = self._detect_building_use(text)
        fields["building_use"] = {
            "value": building_use,
            "confidence": 0.95,
            "label": "கட்டிட பயன்பாடு (Building Use / Occupancy)"
        }

        # 2. Shop Code / Details
        shop_code = self._detect_shop_details(text)
        fields["shop_details"] = {
            "value": shop_code,
            "confidence": 0.92 if shop_code != "Not Specified (-)" else 0.80,
            "label": "கடை / வணிக விவரம் (Shop Code / Details)"
        }

        # 3. Standard Planning & Permit Fields
        standard_patterns = [
            ("permit_number", "அனுமதி எண் (Planning Permit / Sanction No)", [
                r'(?:permit|sanction|approval|order)\s*(?:no|number|ref)[^\n:]*[:\s]+([^\n,]+)',
                r'(?:திட்ட\s*அனுமதி|கட்டிட\s*அனுமதி)\s*எண்[^\n:]*[:\s]+([^\n,]+)'
            ]),
            ("applicant_name", "விண்ணப்பதாரர் (Applicant / Owner Name)", [
                r'(?:applicant|owner|developer|builder)\s*(?:name)?[^\n:]*[:\s]+([^\n,]+)',
                r'(?:விண்ணப்பதாரர்|உரிமையாளர்)\s*பெயர்[^\n:]*[:\s]+([^\n,]+)'
            ]),
            ("survey_number", "சர்வே எண் (Survey / Plot No)", [
                r'(?:survey\s*(?:no|number)|s\.?\s*no)[^\n:]*[:\s]+([0-9A-Za-z\/\-]+(?:\s*(?:pt|part))?)',
                r'(?:புல\s*எண்|சர்வே\s*எண்)[^\n:]*[:\s]+([0-9A-Za-z\/\-]+)'
            ]),
            ("plot_details", "மனை விவரம் (Plot / Door / Site Details)", [
                r'(?:plot|site|door)\s*(?:no|number|details)[^\n:]*[:\s]+([^\n]+)',
                r'(?:மனை\s*எண்|கதவு\s*எண்)[^\n:]*[:\s]+([^\n]+)'
            ]),
            ("built_up_area", "கட்டிய பரப்பு (Built-up Area / Plinth Area)", [
                r'(?:built.?up|plinth|total\s*floor)\s*(?:area)[^\n:]*[:\s]+([^\n]+)',
                r'(?:கட்டிய\s*பரப்பு|தளப்பரப்பு)[^\n:]*[:\s]+([^\n]+)'
            ]),
            ("fsi", "தள பரப்பு குறியீடு (FSI / FAR)", [
                r'(?:fsi|far|floor\s*area\s*ratio)[^\n:]*[:\s]+([0-9\.\/]+[^\n]*)',
                r'(?:தளப்\s*பரப்புக்\s*குறியீடு)[^\n:]*[:\s]+([^\n]+)'
            ]),
            ("approval_authority", "அங்கீகரித்த அமைப்பு (Approval Authority)", [
                r'(CMDA|DTCP|Greater\s*Chennai\s*Corporation|Corporation\s*of\s*Chennai|Municipality|Town\s*Panchayat|பெருநகர\s*சென்னை\s*மாநகராட்சி|நகராட்சி|உள்ளாட்சி\s*அமைப்பு)',
                r'(?:authority|sanctioning\s*body)[^\n:]*[:\s]+([^\n]+)'
            ]),
            ("approval_date", "அனுமதி நாள் (Approval / Sanction Date)", [
                r'(?:dated?|sanction\s*date|approval\s*date)[^\n:]*[:\s]+((?:0[1-9]|[12][0-9]|3[01])[\-\/.](?:0[1-9]|1[0-2])[\-\/.](?:19|20)\d{2})',
                r'((?:0[1-9]|[12][0-9]|3[01])[\-\/.](?:0[1-9]|1[0-2])[\-\/.](?:19|20)\d{2})'
            ]),
        ]

        for key, label, patterns in standard_patterns:
            val = self._find_value(text, patterns)
            fields[key] = {
                "value": val or "Not Detected",
                "confidence": 0.90 if val else 0.0,
                "label": label
            }

        return fields
