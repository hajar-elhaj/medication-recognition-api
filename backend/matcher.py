"""Pin down the exact medicine variant (dosage + form) from noisy OCR text.

The CNN gives us the medicine NAME, which narrows the database to that
medicine's variants. This module reads the OCR text to extract the dosage
(e.g. "400mg") and the form (e.g. "comprimé pelliculé") and matches them
against those variants to identify the exact one.
"""
import re
import unicodedata

from rapidfuzz import fuzz


def _strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def _word_candidates(text, pattern):
    """Words matching `pattern` plus adjacent pairs (covers names OCR splits)."""
    words = re.findall(pattern, text)
    return list(words) + [
        f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)
    ]


def match_name(ocr_text, known_names, name_ar=None,
               threshold=82, floor=65, margin=12):
    """Identify the medicine NAME from the OCR text via fuzzy matching.

    The medicine name is printed on the box, so the OCR text is the most
    reliable source of the name — far more so than the CNN, which only sees
    the image visually. We compare each known DB name against every word (and
    adjacent word pair) in the OCR text, tolerating OCR typos and brand
    spelling differences (e.g. "Ventolin" on the box vs "Ventoline" in the DB).

    `name_ar` is an optional {latin_name: arabic_name} map so Arabic-only boxes
    (e.g. "دوليبران" with no Latin name) are matched against the Arabic name and
    still resolve to the canonical Latin name.

    A name is accepted when EITHER:
      - its score clears `threshold` (a clear, confident read), OR
      - its score is at least `floor` AND beats the next-best medicine by
        `margin`. This rescues blurry boxes where OCR garbles the name (e.g.
        "AlucMENTIN" scores ~73) but it is still unmistakably ahead of every
        other medicine — far better than falling back to the unreliable CNN.

    Returns (best_name, best_score). best_name is None if nothing qualifies.
    """
    name_ar = name_ar or {}
    # Latin words (accent-stripped, lower-cased) and Arabic words, separately.
    latin_cands = _word_candidates(_strip_accents(ocr_text.lower()), r"[a-z]+")
    arabic_cands = _word_candidates(ocr_text, r"[؀-ۿ]+")

    # Best fuzzy score for each known medicine.
    scores = {}
    for name in known_names:
        targets = [(_strip_accents(name.lower()), latin_cands)]
        if name_ar.get(name):
            targets.append((name_ar[name], arabic_cands))
        scores[name] = max(
            (fuzz.ratio(t, c) for t, cands in targets for c in cands),
            default=0,
        )

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_name, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    accepted = best_score >= threshold or (
        best_score >= floor and best_score - second_score >= margin
    )
    return (best_name, best_score) if accepted else (None, best_score)


# OCR keyword (accent-free) -> canonical French form.
# Order matters: more specific first, because e.g. "comprimé pelliculé" also
# contains the word "comprimé", and "suspension pour inhalation" contains
# "suspension".
_FORM_KEYWORDS = [
    # French (accent-free)
    ("pellicul", "comprimé pelliculé"),
    ("effervescent", "comprimé effervescent"),
    ("inhalation", "inhalateur"),
    ("pressuris", "inhalateur"),
    ("inhalateur", "inhalateur"),
    ("injectable", "solution injectable"),
    ("ampoule", "solution injectable"),
    ("gelule", "gélule"),
    ("sachet", "sachet"),
    ("suppositoire secable", "suppositoire sécable"),
    ("suppositoire", "suppositoire"),
    ("suspension buvable", "sirop"),
    ("sirop", "sirop"),
    ("comprime", "comprimé"),
    # Arabic (specific forms before generic). Accent-stripping also normalises
    # Arabic hamza variants (e.g. أ -> ا), so plain spellings match.
    ("قرص مغلف", "comprimé pelliculé"),
    ("قرص فوار", "comprimé effervescent"),
    ("مغلف", "comprimé pelliculé"),
    ("فوار", "comprimé effervescent"),
    ("كبسولة", "gélule"),
    ("استنشاق", "inhalateur"),
    ("بخاخ", "inhalateur"),
    ("حقن", "solution injectable"),
    ("امبولة", "solution injectable"),
    ("كيس", "sachet"),
    ("شراب", "sirop"),
    ("تحميلة قابلة للتقسيم", "suppositoire sécable"),
    ("تحميلة", "suppositoire"),
    ("لبوس", "suppositoire"),
    ("قرص", "comprimé"),
]


# Long-form and symbol unit aliases → canonical Latin unit. Order matters:
# microgram variants must come before "mg", and longer Arabic spellings before
# shorter ones (e.g. ملجم before مل) so prefixes don't get replaced first.
_UNIT_ALIASES = [
    # microgram — must come before mg/gram rules
    ("microgrammes", "mcg"), ("microgramme", "mcg"),
    ("micrograms",   "mcg"), ("microgram",   "mcg"),
    ("µg", "mcg"), ("ug", "mcg"),
    ("ميكروغرام", "mcg"), ("ميكروجرام", "mcg"),
    ("مكجم", "mcg"), ("مكغ", "mcg"),
    # milligram — several spellings (مجم, ملجم, ملغم, ملغ). These must come
    # before "مل" (millilitre, a prefix of some) and before "جم"/"غ" (gram,
    # substrings of مجم/ملغم) so they aren't partially replaced first.
    ("مجم", "mg"), ("ملجم", "mg"), ("ملغم", "mg"), ("ملغ", "mg"),
    # millilitre
    ("مل",   "ml"),
    # gram — single letters last
    ("جم",   "g"),  ("غ",  "g"),
]

# Two visually-similar but distinct Unicode digit sets map to Western digits:
#   Eastern Arabic-Indic ٠-٩ (U+0660–0669) — common on Arab-market packaging
#   Persian/Urdu         ۰-۹ (U+06F0–06F9) — EasyOCR's Arabic engine often
#                                            returns these instead.
_ARABIC_DIGITS = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩" "۰۱۲۳۴۵۶۷۸۹",
    "0123456789" "0123456789",
)


def _normalize_units(text):
    """Lower-case, strip accents, convert Arabic-Indic digits, and map every
    unit alias (microgrammes, µg, ملغ, …) to its canonical Latin form. Shared
    by extract_dosages() and the fallback so both see the same units."""
    t = text.translate(_ARABIC_DIGITS)
    t = _strip_accents(t.lower())
    for alias, canonical in _UNIT_ALIASES:
        t = t.replace(alias, canonical)
    return t


def extract_dosages(text):
    """Return dosage tokens found in OCR text, e.g. ['400mg', '1g'].

    Strong signal: the number and unit are adjacent (e.g. "400 mg").
    Supports Latin units (mg, ml, g, mcg), long forms (microgrammes), symbols
    (µg) and Arabic equivalents (ملغ/ملجم = mg, مل = ml, …).
    """
    t = _normalize_units(text)
    # The number and unit may be separated only by whitespace — NOT by other
    # words/numbers. (Stripping all spaces would glue an unrelated number, e.g.
    # an "autorisé n° 3400934438738", onto the real dosage.) The trailing \b
    # stops a unit from matching inside another word, e.g. "100 gouttes".
    found = re.findall(r"(\d+(?:[.,]\d+)?)\s*(mcg|mg|ml|g)\b", t)
    return [f"{num.replace(',', '.')}{unit}" for num, unit in found]


def _numbers_in(text):
    """Return the set of standalone numbers in the text, e.g. {'500', '27'}."""
    return {n.replace(",", ".") for n in re.findall(r"\d+(?:[.,]\d+)?", text)}


def _dosage_parts(dosage):
    """Split a stored dosage like '500mg' into ('500', 'mg'); else (None, None)."""
    m = re.match(r"(\d+(?:[.,]\d+)?)\s*([a-z]+)", (dosage or "").lower())
    if m:
        return m.group(1).replace(",", "."), m.group(2)
    return None, None


def detect_form(text):
    """Return the canonical form detected in OCR text, or None."""
    norm = _strip_accents(text.lower())
    for keyword, form in _FORM_KEYWORDS:
        if keyword in norm:
            return form
    return None


def identify_variant(ocr_text, variants):
    """Narrow a medicine's variants to the exact one using OCR text.

    `variants` is a list of dicts with keys 'dosage', 'form', 'form_ar'.

    Returns a dict:
      exact      -> the single matched variant, or None if not uniquely resolved
      candidates -> the remaining (narrowed) variants
      dosage     -> the dosage detected in the OCR text, or None
      form       -> the form detected in the OCR text, or None
    """
    dosages = extract_dosages(ocr_text)
    form = detect_form(ocr_text)

    candidates = list(variants)

    matched_dosage = None
    # 1. Strong signal: an adjacent "<number><unit>" token (e.g. "500mg")
    #    that matches a candidate's dosage exactly.
    for d in dosages:
        narrowed = [v for v in candidates if v["dosage"].lower() == d.lower()]
        if narrowed:
            candidates = narrowed
            matched_dosage = d
            break
    else:
        # 2. Fallback: OCR often splits the number from its unit (e.g. reads
        #    "500" near the title and "mg" elsewhere on the box). Match a
        #    candidate's dosage number against the standalone numbers in the
        #    text, but only if that candidate's unit also appears somewhere —
        #    this rejects pack counts like "12 sachets" or "dès 27 kg".
        norm = _normalize_units(ocr_text)
        numbers = _numbers_in(norm)
        matching = []
        for v in candidates:
            num, unit = _dosage_parts(v["dosage"])
            if num and num in numbers and (not unit or unit in norm):
                matching.append(v)
        if matching and len(matching) < len(candidates):
            candidates = matching
            distinct = {v["dosage"] for v in matching}
            if len(distinct) == 1:
                matched_dosage = next(iter(distinct))

    if form:
        narrowed = [v for v in candidates if v["form"] == form]
        if narrowed:
            candidates = narrowed

    # Only declare an EXACT variant when we have real evidence of the DOSAGE
    # (the safety-critical field we actually read from the box), OR when the
    # medicine has a single variant anyway so there's nothing to disambiguate.
    # Narrowing to one candidate by FORM alone is NOT enough: a misread form
    # would otherwise yield a confident but wrong dosage (e.g. an injectable
    # box reported as "2mg sirop" just because sirop is the only sirop variant).
    resolved = matched_dosage is not None or len(variants) == 1
    exact = candidates[0] if (len(candidates) == 1 and resolved) else None
    return {
        "exact": exact,
        "candidates": candidates,
        "dosage": matched_dosage,
        "form": form,
    }
