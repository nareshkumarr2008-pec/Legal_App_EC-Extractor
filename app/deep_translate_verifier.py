# -*- coding: utf-8 -*-
"""
Offline bilingual verification layer for Executant / Claimant party names
in the EC (Encumbrance Certificate) pipeline.

For every party name this module produces BOTH scripts (English + Tamil)
and cross-checks the translation with a round-trip back-translation:

    Tamil name --translate--> English name --translate back--> Tamil'
    compare(Tamil, Tamil') -> similarity score -> verified / needs review

This does not "prove" a translation is correct, but it reliably flags the
entries where the round trip drifted a lot, so a reviewer only has to look
at the ones actually worth checking instead of every single row.

Engines (in order, each result is cached so the same name is only ever
looked up once across the whole app's lifetime):
    1. IndicTrans2 (AI4Bharat) neural NMT — app/indic_translator.py.
       Runs fully locally once the models are cached (no network calls,
       no rate limits), and is materially more accurate on Tamil proper
       nouns / legal terminology than generic MT engines.
    2. Local dictionary + phonetic engine already in app/translator.py
       (always available, zero network / zero model load, used whenever
       IndicTrans2's models aren't installed/downloaded yet — e.g. first
       run before `torch`/`transformers` are set up — so the app never
       breaks or hangs on this step)

This module makes NO outbound network calls. On-disk caching still keeps
repeated names / recurring villages / banks fast (skips re-running the
model), but there is no rate limit to worry about any more.
"""

import json
import logging
import re
import threading
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

from app.translator import (
    dynamic_transliterate_tamil,
    dynamic_english_to_tamil,
    clean_initials_and_dots,
    normalize_tamil_visual_order,
    _strip_stray_script_marks,
)
from app.indic_translator import (
    translate_to_tamil as _it2_to_tamil,
    translate_to_english as _it2_to_english,
    is_available as _it2_available,
)

TAMIL_RE = re.compile(r'[\u0b80-\u0bff]')
LATIN_RE = re.compile(r'[A-Za-z]')

# Bilingual "X (Y)" parsing — allow stray spaces right after '(' since OCR
# often leaves one, e.g. "அலேக் குமார் குலிசா ( Alok Kumar Gulechha)"
_TA_EN_PAREN = re.compile(r'^([\u0b80-\u0bff][\u0b80-\u0bff\s\.]*?)\s*\(\s*([A-Za-z][A-Za-z\s\.]*?)\s*\)\s*$')
_EN_TA_PAREN = re.compile(r'^([A-Za-z][A-Za-z\s\.]*?)\s*\(\s*([\u0b80-\u0bff][\u0b80-\u0bff\s\.]*?)\s*\)\s*$')

# Known role / designation tags that ride along with a party name in
# brackets — these are looked up in a fixed glossary rather than sent
# through the translator, since they're a closed, well-known vocabulary.
ROLE_CANON: Dict[str, Tuple[str, str]] = {
    # "பிரின்சிபல்" (Prin-ci-pal) is the correct transliteration -- the
    # legacy spelling "பிரின்ஸ்பால்" (Prin-s-paal) dropped the "சி" (ci)
    # syllable entirely. Kept as a recognized input alias below (mapping TO
    # the correct spelling) so any already-stored data using the old
    # spelling still matches; only the OUTPUT spelling changes.
    "principal": ("Principal", "பிரின்சிபல்"),
    "பிரின்சிபல்": ("Principal", "பிரின்சிபல்"),
    "பிரின்ஸ்பால்": ("Principal", "பிரின்சிபல்"),  # legacy misspelling, input-only
    "முதல்வர்": ("Principal", "பிரின்சிபல்"),
    "agent": ("Agent", "ஏஜண்ட்"),
    "ஏஜண்ட்": ("Agent", "ஏஜண்ட்"),
    "ஏஜெண்ட்": ("Agent", "ஏஜண்ட்"),
    "ஏெஜண்ட்": ("Agent", "ஏஜண்ட்"),
    "ejend": ("Agent", "ஏஜண்ட்"),
    "முகவர்": ("Agent", "முகவர்"),
    "vendor": ("Vendor", "விற்பவர்"),
    "விற்பவர்": ("Vendor", "விற்பவர்"),
    "purchaser": ("Purchaser", "வாங்குபவர்"),
    "வாங்குபவர்": ("Purchaser", "வாங்குபவர்"),
    "witness": ("Witness", "சாட்சி"),
    "சாட்சி": ("Witness", "சாட்சி"),
    "gpa holder": ("GPA Holder", "ஜிபிஏ வைத்தவர்"),
    "power of attorney": ("GPA Holder", "ஜிபிஏ வைத்தவர்"),
    "mortgagor": ("Mortgagor", "அடமானம் வைத்தவர்"),
    "mortgagee": ("Mortgagee", "அடமானம் பெற்றவர்"),
    "legal heir": ("Legal Heir", "சட்டப்பூர்வ வாரிசு"),
    "doctor": ("Doctor", "டாக்டர்"),
    "dr": ("Dr.", "டாக்டர்"),
    "dr.": ("Dr.", "டாக்டர்"),
    "டாக்டர்": ("Dr.", "டாக்டர்"),

    # Lease roles (Lessor / Lessee)
    "lessor": ("Lessor", "குத்தகைக்கு விட்டவர்"),
    "lessee": ("Lessee", "குத்தகைக்கு எடுத்தவர்"),
    "lessors": ("Lessor", "குத்தகைக்கு விட்டவர்"),
    "lessees": ("Lessee", "குத்தகைக்கு எடுத்தவர்"),
    "குத்தகைக்கு விட்டவர்": ("Lessor", "குத்தகைக்கு விட்டவர்"),
    "குத்தகை கொடுத்தவர்": ("Lessor", "குத்தகைக்கு விட்டவர்"),
    "குத்தகை கொடுப்பவர்": ("Lessor", "குத்தகைக்கு விட்டவர்"),
    "குத்தகை அளித்தவர்": ("Lessor", "குத்தகைக்கு விட்டவர்"),
    "குத்தகைக்கு எடுத்தவர்": ("Lessee", "குத்தகைக்கு எடுத்தவர்"),
    "குத்தகைதாரர்": ("Lessee", "குத்தகைக்கு எடுத்தவர்"),
    "குத்தகைதாரர்கள்": ("Lessee", "குத்தகைக்கு எடுத்தவர்"),
    "குத்தகை வாங்கியவர்": ("Lessee", "குத்தகைக்கு எடுத்தவர்"),

    # Party designations (1st Party, 2nd Party, 3rd Party)
    "1 வது பார்ட்டி": ("1st Party", "1வது தரப்பினர்"),
    "1வது பார்ட்டி": ("1st Party", "1வது தரப்பினர்"),
    "1vathu paartti": ("1st Party", "1வது தரப்பினர்"),
    "2 வது பார்ட்டி": ("2nd Party", "2வது தரப்பினர்"),
    "2வது பார்ட்டி": ("2nd Party", "2வது தரப்பினர்"),
    "2vathu paartti": ("2nd Party", "2வது தரப்பினர்"),
    "3 வது பார்ட்டி": ("3rd Party", "3வது தரப்பினர்"),
    "3வது பார்ட்டி": ("3rd Party", "3வது தரப்பினர்"),
    "3vathu paartti": ("3rd Party", "3வது தரப்பினர்"),
    "1st party": ("1st Party", "1வது தரப்பினர்"),
    "2nd party": ("2nd Party", "2வது தரப்பினர்"),
    "3rd party": ("3rd Party", "3வது தரப்பினர்"),
}

# --------------------------------------------------------------------
# On-disk cache — one JSON file, loaded once, shared for the process
# lifetime. Every (text, direction) pair is looked up here first, so a
# name repeated across many EC entries / many documents costs exactly
# one outbound network call ever.
# --------------------------------------------------------------------
_CACHE_PATH = Path(__file__).resolve().parent.parent / "runtime_cache" / "deep_translate_cache.json"
_cache_lock = threading.Lock()
_cache: Dict[str, str] = {}
_cache_loaded = False


def _load_cache() -> None:
    global _cache_loaded
    if _cache_loaded:
        return
    with _cache_lock:
        if _cache_loaded:
            return
        try:
            if _CACHE_PATH.exists():
                _cache.update(json.loads(_CACHE_PATH.read_text(encoding="utf-8")))
        except Exception as e:
            logger.warning(f"deep_translate cache load failed: {e}")
        _cache_loaded = True


def _save_cache() -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _cache_lock:
            _CACHE_PATH.write_text(json.dumps(_cache, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.warning(f"deep_translate cache save failed: {e}")


def _cache_key(text: str, direction: str) -> str:
    return f"{direction}::{text.strip()}"


def _indictrans2_translate(text: str, source: str, target: str) -> Optional[str]:
    """
    Run the local IndicTrans2 model (source/target are 'en'/'ta').
    Returns None if the models aren't available (e.g. torch/transformers not
    installed yet, or model weights not downloaded) so the caller can fall
    back to the local rule-based engine. No network calls happen here — the
    models, once downloaded once via huggingface-hub, are read from the
    on-disk HF cache.
    """
    text = text.strip()
    if not text or not _it2_available():
        return None
    try:
        if source == "en" and target == "ta":
            result = _it2_to_tamil(text)
        elif source == "ta" and target == "en":
            result = _it2_to_english(text)
        else:
            return None
        return result.strip() if result else None
    except Exception as e:
        logger.info(f"IndicTrans2 {source}->{target} failed for {text!r}: {e}")
        return None


def _translate_cached(text: str, source: str, target: str) -> Tuple[str, str]:
    """
    Returns (translation, engine). engine is one of:
    'cache', 'indictrans2', 'local'. Never returns None — always falls
    back to the local rule-based engine so the app keeps working even
    before the IndicTrans2 models are downloaded.
    """
    text = (text or "").strip()
    if not text:
        return "", "n/a"

    _load_cache()
    key = _cache_key(text, f"{source}->{target}")
    with _cache_lock:
        cached = _cache.get(key)
    if cached is not None:
        return cached, "cache"

    result = _indictrans2_translate(text, source, target)
    engine = "indictrans2"
    if not result:
        result = dynamic_transliterate_tamil(text) if target == "en" else dynamic_english_to_tamil(text)
        engine = "local"

    if result:
        with _cache_lock:
            _cache[key] = result
        _save_cache()
    return (result or text), engine


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


_PHONETIC_LOANWORD_FIXES = {
    "pisnas": "Business",
    "pisinas": "Business",
    "menajmend": "Management",
    "menejmend": "Management",
    "sarvees": "Services",
    "sarvis": "Services",
    "piraivad": "Private",
    "piraivet": "Private",
    "piraievad": "Private",
    "limided": "Limited",
    "limidat": "Limited",
    "snago": "Sneha",
    "snega": "Sneha",
    "snegaa": "Sneha",
    "piragaash": "Prakash",
    "piragash": "Prakash",
    "piragaas": "Prakash",
    "pirakaash": "Prakash",
    "uthraa": "Uthra",

    # English / Biblical "za" names
    "elisapath": "Elizabeth",
    "elisapeth": "Elizabeth",
    "elisapat": "Elizabeth",
    "elisaapath": "Elizabeth",
    "elisaapeth": "Elizabeth",

    # Arabic / Persian / Urdu / Indian "za" names
    "mirsa": "Mirza",
    "mirsaa": "Mirza",
    "mirja": "Mirza",
    "hamsa": "Hamza",
    "hamsaa": "Hamza",
    "paisal": "Faizal",
    "paizal": "Faizal",
    "faisal": "Faizal",
    "faizal": "Faizal",
    "rasa": "Raza",
    "rasaa": "Raza",
    "rasak": "Razak",
    "rasaak": "Razak",
    "parsaanaa": "Farzana",
    "parsana": "Farzana",
    "riyaas": "Riyaz",
    "riyas": "Riyaz",
    "riyaaj": "Riyaz",
    "riyaj": "Riyaz",
    "peros": "Feroz",
    "piros": "Feroz",
    "feroze": "Feroz",
    "ajees": "Aziz",
    "asees": "Aziz",
    "azeez": "Aziz",
    "mumtaaj": "Mumtaz",
    "mumtaas": "Mumtaz",
    "navaas": "Nawaz",
    "navaaj": "Nawaz",
    "shaanavaas": "Shahnawaz",
    "shanavaas": "Shahnawaz",
    "imthiyaas": "Imtiaz",
    "imthiyas": "Imtiaz",
    "imtiyaas": "Imtiaz",
    "imtiyas": "Imtiaz",
    "imtiyaj": "Imtiaz",
    "ayaas": "Ayaz",
    "ayas": "Ayaz",
    "sarparaas": "Sarfaraz",
    "sarfaraas": "Sarfaraz",
    "parves": "Parvez",
    "parvej": "Parvez",
    "musaapar": "Muzaffar",
    "musapar": "Muzaffar",
    "agamathu": "Ahamed",
    "agmathu": "Ahamed",

    # Banking and company loanwords / OCR typos
    "kodtag": "Kotak",
    "kodak": "Kotak",
    "meganthiraa": "Mahindra",
    "meganthira": "Mahindra",
    "paang": "Bank",
    "paangk": "Bank",
    "ladsumi": "Lakshmi",
    "lashmi": "Lakshmi",
    "jenaral": "General",
    "peng": "Bank",
    "penk": "Bank",
    "esteds": "Estates",
    "estads": "Estates",
    "foundatiosn": "Foundations",
    "pavundeshan": "Foundations",
    "pavunteshon": "Foundations",
    "pavundeson": "Foundations",
    "pvt": "Pvt",
    "ltd": "Ltd",

    # Key personal names
    "hinduja": "Hinduja",
    "inthujaa": "Hinduja",
    "inthuja": "Hinduja",
    "neetu": "Neetu",
    "neethu": "Neetu",
    "needu": "Neetu",
    "lasardo": "Lasrado",
    "lasrado": "Lasrado",
}


def _titlecase_name(name: str) -> str:
    if not name:
        return name
    cleaned = clean_initials_and_dots(name)
    cleaned = _strip_stray_script_marks(cleaned)
    words = cleaned.split()
    out = []
    for w in words:
        # Separate leading/trailing punctuation like ( or ) or , or ;
        m_punct = re.match(r'^([(\[\{"\']*)\s*(.*?)\s*([)\]\}"\',;]*)$', w)
        if m_punct:
            pre, core, post = m_punct.group(1), m_punct.group(2), m_punct.group(3)
        else:
            pre, core, post = "", w, ""

        core_low = core.lower()
        if re.match(r'^(?:[A-Z]\.)+$', core):
            c_out = core
        elif core_low in ("dr.", "dr"):
            c_out = "Dr."
        elif core == "&":
            c_out = "&"
        elif core.upper() in ("LLP", "PVT", "LTD", "GPA", "SBI", "HDFC", "ICICI"):
            c_out = core.upper()
        elif core_low in _PHONETIC_LOANWORD_FIXES:
            c_out = _PHONETIC_LOANWORD_FIXES[core_low]
        elif re.match(r'^[A-Za-z]\.?$', core):
            c_out = core.upper() + ('' if core.endswith('.') else '.')
        else:
            c_out = core.capitalize() if core else ""

        out.append(f"{pre}{c_out}{post}" if (pre or post) else c_out)
    return " ".join(out)


VERIFY_THRESHOLD = 60  # confidence % at/above which a round-trip is "verified"

# Known bilingual institution names — looked up BEFORE any translation engine
# so they're never re-phonetically-transliterated incorrectly.
KNOWN_INSTITUTIONS: Dict[str, Tuple[str, str]] = {
    "shrine velankanni senior secondary school": (
        "Shrine Velankanni Senior Secondary School",
        "ஷ்ரைன் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்"
    ),
    "sherin velankanni senior secondary school": (
        "Shrine Velankanni Senior Secondary School",
        "ஷ்ரைன் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்"
    ),
    "chennai shrine velankanni senior secondary school": (
        "Chennai Shrine Velankanni Senior Secondary School",
        "சென்னை ஷ்ரைன் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்"
    ),
    "kotak mahindra bank limited": (
        "Kotak Mahindra Bank Limited",
        "கோட்டக் மகிந்திரா பாங்க் லிமிடெட்"
    ),
    "kotak mahindra bank": (
        "Kotak Mahindra Bank",
        "கோட்டக் மகிந்திரா பாங்க்"
    ),
    "kodtag meganthiraa paang": (
        "Kotak Mahindra Bank",
        "கோட்டக் மகிந்திரா பாங்க்"
    ),
    "kodtag meganthiraa paang limited": (
        "Kotak Mahindra Bank Limited",
        "கோட்டக் மகிந்திரா பாங்க் லிமிடெட்"
    ),
    "icici bank limited": (
        "ICICI Bank Limited",
        "ஐ.சி.ஐ.சி.ஐ வங்கி லிமிடெட்"
    ),
    # Mixed Tamil+Latin OCR form: ஐ.C.ஐ.C.ஐ
    "ஐ.c.ஐ.c.ஐ வங்கி": (
        "ICICI Bank",
        "ஐ.சி.ஐ.சி.ஐ வங்கி"
    ),
    "ai c. ai c. ai bank": (
        "ICICI Bank",
        "ஐ.சி.ஐ.சி.ஐ வங்கி"
    ),
    "ai.c. ai.c. ai bank": (
        "ICICI Bank",
        "ஐ.சி.ஐ.சி.ஐ வங்கி"
    ),
    "laksumi general finance limited": (
        "Lakshmi General Finance Limited",
        "லட்சுமி ஜெனரல் பைனான்ஸ் லிமிடெட்"
    ),
    "chennai lakshmi general finance limited": (
        "Chennai Lakshmi General Finance Limited",
        "சென்னை லட்சுமி ஜெனரல் பைனான்ஸ் லிமிடெட்"
    ),
    "chennai ladsumi jenaral finance limited": (
        "Chennai Lakshmi General Finance Limited",
        "சென்னை லட்சுமி ஜெனரல் பைனான்ஸ் லிமிடெட்"
    ),
    "chennai m/s. lakshmi general finance limited": (
        "Chennai M/s. Lakshmi General Finance Limited",
        "சென்னை M/s. லஷ்மி ஜெனரல் Finance Limited"
    ),
    "chennai m/s lakshmi general finance limited": (
        "Chennai M/s. Lakshmi General Finance Limited",
        "சென்னை M/s. லஷ்மி ஜெனரல் Finance Limited"
    ),
    "chennai mesars lakshmi general finance limited": (
        "Chennai M/s. Lakshmi General Finance Limited",
        "சென்னை M/s. லஷ்மி ஜெனரல் Finance Limited"
    ),
    "chennai siraiyil velankanni senior secondary school": (
        "Chennai Siraiyil Velankanni Senior Secondary School",
        "சென்னை சிரையில் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்"
    ),
    "chennai siraiyil velankanni senior segastari school": (
        "Chennai Siraiyil Velankanni Senior Secondary School",
        "சென்னை சிரையில் வேளாங்கன்னி சீனியர் செகண்டரி ஸ்கூல்"
    ),
}


def translate_and_verify(raw_text: str) -> Dict:
    """
    Takes one name (Tamil, English, or already-bilingual "X (Y)") and returns
    a bilingual, back-translation-verified record:
        {original, english, tamil, verified, confidence, engine}
    """
    raw = (raw_text or "").strip()
    if not raw or raw in ("-", "Not Detected"):
        empty = raw or "-"
        return {"original": raw, "english": empty, "tamil": empty,
                "verified": False, "confidence": 0, "engine": "n/a"}

    # --- Known institution fast-path ---
    # Strip any trailing role tags first so "Kotak Mahindra Bank Limited (Principal) Sridhar (Agent)" matches
    clean_raw_for_inst, inst_role_en, inst_role_ta = _strip_trailing_roles(raw)
    raw_lower = re.sub(r'\s+', ' ', clean_raw_for_inst).strip().lower()
    # Normalize Tamil/English transliteration artifacts for key lookup
    raw_lower_norm = (raw_lower.replace('ஐ.c.ஐ.c.ஐ', 'icici')
                      .replace('ai c. ai c. ai', 'icici')
                      .replace('kodtag', 'kotak')
                      .replace('meganthiraa', 'mahindra')
                      .replace('paang', 'bank')
                      .replace('ladsumi', 'lakshmi')
                      .replace('jenaral', 'general')
                      .replace('சென்னை', 'chennai')
                      .replace('லட்சுமி', 'lakshmi')
                      .replace('லஷ்மி', 'lakshmi')
                      .replace('ஜெனரல்', 'general')
                      .replace('பைனான்ஸ்', 'finance')
                      .replace('லிமிடெட்', 'limited')
                      .replace('லிட்', 'limited'))

    for key, (eng, tam) in KNOWN_INSTITUTIONS.items():
        key_norm = (key.replace('ஐ.c.ஐ.c.ஐ', 'icici')
                    .replace('kodtag', 'kotak')
                    .replace('meganthiraa', 'mahindra')
                    .replace('paang', 'bank')
                    .replace('ladsumi', 'lakshmi')
                    .replace('jenaral', 'general'))
        if (key in raw_lower or raw_lower in key or
                key_norm in raw_lower_norm or raw_lower_norm in key_norm or
                ('icici' in raw_lower_norm and 'icici' in key_norm)):
            return {
                "original": raw,
                "english": eng,
                "tamil": tam,
                "verified": True,
                "confidence": 100,
                "engine": "glossary",
            }

    raw_clean = clean_initials_and_dots(raw)
    engine = "parsed"
    m1 = _TA_EN_PAREN.match(raw_clean)
    m2 = _EN_TA_PAREN.match(raw_clean)

    if m1:
        tamil, english = clean_initials_and_dots(m1.group(1).strip()), _titlecase_name(m1.group(2).strip())
    elif m2:
        english, tamil = _titlecase_name(m2.group(1).strip()), clean_initials_and_dots(m2.group(2).strip())
    else:
        has_ta = bool(TAMIL_RE.search(raw_clean))
        has_en = bool(LATIN_RE.search(raw_clean))
        if has_en and not has_ta:
            english = _titlecase_name(raw_clean)
            tamil, engine = _translate_cached(english, "en", "ta")
            tamil = clean_initials_and_dots(tamil)
        else:
            # Pure Tamil, or mixed (e.g. "G. ராமானுஜம்") — treat as
            # Tamil-primary and translate to English.
            tamil = normalize_tamil_visual_order(raw_clean)
            english, engine = _translate_cached(tamil, "ta", "en")
            english = _titlecase_name(english)

    # --- Back-translation verification: translate the English form back
    # to Tamil and compare it to the Tamil form we're actually reporting.
    back_tamil, _ = _translate_cached(english, "en", "ta")
    back_tamil = clean_initials_and_dots(back_tamil)
    confidence = round(_similarity(tamil, back_tamil) * 100)
    verified = confidence >= VERIFY_THRESHOLD

    return {
        "original": raw_clean,
        "english": english or raw_clean,
        "tamil": tamil or raw_clean,
        "verified": verified,
        "confidence": confidence,
        "engine": engine,
    }


def _strip_trailing_roles(entry: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Strips zero or more trailing "(role)" tags (Principal/Agent/Vendor/...)
    off a party-name entry and returns (remaining_name, role_english, role_tamil).
    Stops at the first trailing paren that is NOT a recognized role — that
    one belongs to the name itself (e.g. an existing bilingual translation).
    """
    s = entry.strip()
    role_en, role_ta = None, None

    # First clean unclosed parens at the end, e.g. "Name Principal)" -> "Name (Principal)"
    s = re.sub(r'(?<![\(\s])(Principal|Agent|Vendor|Purchaser)\)', r' (\1)', s, flags=re.I)

    paren_re = re.compile(r'\(\s*([^()]*?)\s*\)\s*$')
    while True:
        m = paren_re.search(s)
        if not m:
            break
        content = re.sub(r'\s+', ' ', m.group(1).strip())
        canon = ROLE_CANON.get(content) or ROLE_CANON.get(content.lower())
        if not canon and "/" in content:
            for p in content.split("/"):
                p_clean = p.strip()
                canon = ROLE_CANON.get(p_clean) or ROLE_CANON.get(p_clean.lower())
                if canon:
                    break
        if not canon:
            break
        role_en, role_ta = canon
        s = s[:m.start()].strip()
    return s, role_en, role_ta


def bilingual_party_list(raw_field: str) -> List[Dict]:
    """
    Splits an Executant(s)/Claimant(s) OCR string (numbered list convention:
    "1. ... 2. ... 3. ...") into individual parties, each translated and
    back-translation-verified into both English and Tamil.
    """
    if not raw_field or raw_field in ("-", "Not Detected"):
        return []

    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', raw_field.replace('\n', ' ')).strip()

    # Split (Principal) followed by another person (Agent) if not already numbered
    normalized = re.sub(r'(\((?:Principal|பிரின்சிபல்|பிரின்ஸ்பால்)\))\s+(?!\d+\.)', r'\1 2. ', normalized, flags=re.I)
    if re.search(r'\b2\.\s+', normalized) and not re.match(r'^\s*1\.', normalized):
        normalized = '1. ' + normalized

    # Split on numbered list markers: "1.", "2.", "3." etc.
    parts = [p.strip() for p in re.split(r'(?<!\d)\b\d{1,2}\.\s*', normalized) if p.strip()]

    # Deduplicate: skip parts that are pure digit artifacts or already captured
    deduped = []
    for p in parts:
        # Skip standalone page-number artifacts (e.g. "387", "111")
        if re.match(r'^\d{1,4}$', p):
            continue
        # Skip exact duplicates (case-insensitive)
        if not any(p.lower() == d.lower() for d in deduped):
            deduped.append(p)

    out: List[Dict] = []
    for i, part in enumerate(deduped, start=1):
        part_clean_name, role_en, role_ta = _strip_trailing_roles(part)
        if not part_clean_name.strip():
            continue
        rec = translate_and_verify(part_clean_name)
        rec["index"] = i
        rec["role_english"] = role_en
        rec["role_tamil"] = role_ta
        out.append(rec)
    return out
