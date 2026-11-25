"""Cast podcast hosts for a non-English episode.

Catalog voices speak from an English reference sample, so on the cTTS engine
an English voice reading Japanese keeps its English accent. This module picks,
for each host, a voice that is native to the host's language when one is
available, and otherwise the voice the skill would use anyway, with a
description that asks it to speak the language like a native speaker
(``style``; ``references/podcast_native_styles.json``). generate sends that
description with the voice on the cTTS route. This module only reads files and
never designs, saves or activates a voice itself.

Per host, the first matching rule wins:

1. ``user``: a voice the user named for this host (``current`` is Muse's voice).
2. ``series``: the series' established voice.
3. A host the user gave another language (``--host-language``, for a bilingual
   show) is planned by these same rules in that language; an English host
   keeps today's English choices.
4. ``current``: Muse's own voice hosts when it is native to the language
   (not when the user asked for new voices or described this host).
5. ``saved``: a saved voice tagged with the language and variety.
6. ``library``: a catalog voice whose conditioning prompt is in the language;
   a host the user described gets candidates to choose from by description.
7. ``fallback``: a native voice of another variety of the language (Canadian
   French for French). A host the user asked to have an accent (``--accent``)
   gets a library voice with that accent when one exists; an accent no library
   voice has, such as "québécois" for French, is cast as if none was asked.
8. ``styled``: the skill's usual voice, Muse's voice for the main host and the
   podcast shortlist (``references/podcast_preferred_voices.json``) for the
   others, honouring the planned gender. A described host gets candidates among
   the American English library voices.

Every host whose voice doesn't speak its language natively gets ``style``: a
voice the user chose, a series voice, a ``styled`` voice. A host with a
requested accent and the English host of a bilingual show get none, and are
listed in ``no_style`` for generate.

An English episode keeps the skill's existing casting rules, except where the
request names an English variety or accent the library has voices for: a
region in ``--language`` or ``--locale`` (``en-SG`` for Singapore English or
Singlish, ``en-IN``, ``en-GB``, ``en-AU`` and the others in
``references/podcast_english_varieties.json``), or ``--accent`` for a host.
Those hosts get ``variety``: Muse's own voice when it already has that accent,
else the library voices with that accent label, in catalog order. Plain US English, and a region only the UI locale carries, keep
today's rules.
"""

import hashlib
import json
import os
import re
import time
import unicodedata
from pathlib import Path

# Base language -> (English name, default region, ISO 639-3 codes used by the
# catalog's `language` field). Matches tts-cli's ctts::SUPPORTED_LANGUAGES.
LANGUAGES = {
    "ar": ("Arabic", None, ("ara", "arb")),
    "bn": ("Bengali", "BD", ("ben",)),
    "de": ("German", "DE", ("deu", "ger")),
    "en": ("English", "US", ("eng",)),
    "es": ("Spanish", "MX", ("spa",)),
    "fr": ("French", "FR", ("fra", "fre")),
    "he": ("Hebrew", "IL", ("heb",)),
    "hi": ("Hindi", "IN", ("hin",)),
    "id": ("Indonesian", "ID", ("ind",)),
    "it": ("Italian", "IT", ("ita",)),
    "ja": ("Japanese", "JP", ("jpn",)),
    "kn": ("Kannada", "IN", ("kan",)),
    "ko": ("Korean", "KR", ("kor",)),
    "mr": ("Marathi", "IN", ("mar",)),
    "ms": ("Malay", "MY", ("msa", "zsm")),
    "nl": ("Dutch", "NL", ("nld", "dut")),
    "pl": ("Polish", "PL", ("pol",)),
    "pt": ("Portuguese", "BR", ("por",)),
    "ta": ("Tamil", "IN", ("tam",)),
    "te": ("Telugu", "IN", ("tel",)),
    "th": ("Thai", "TH", ("tha",)),
    "tl": ("Tagalog", "PH", ("tgl", "fil")),
    "tr": ("Turkish", "TR", ("tur",)),
    "vi": ("Vietnamese", "VN", ("vie",)),
    "zh": ("Chinese", "CN", ("zho", "cmn", "chi")),
}

# Other codes for supported languages (old ISO 639-1, ISO 639-3, macrolanguage).
ALIASES = {"fil": "tl", "iw": "he", "in": "id", "cmn": "zh", "zho": "zh", "jpn": "ja", "kor": "ko"}

ISO3_TO_BASE = {iso3: base for base, (_, _, codes) in LANGUAGES.items() for iso3 in codes}

# How the plan names the variety. Keys are (base, region); a missing
# region uses the (base, None) entry or the plain language name.
VARIETY = {
    ("ar", None): "Modern Standard Arabic",
    ("ar", "EG"): "Egyptian Arabic",
    ("ar", "SA"): "Gulf Arabic, as spoken in Saudi Arabia",
    ("ar", "AE"): "Gulf Arabic, as spoken in the Emirates",
    ("ar", "MA"): "Moroccan Arabic",
    ("ar", "LB"): "Levantine Arabic, as spoken in Lebanon",
    ("de", "DE"): "standard German, as spoken in Germany",
    ("de", "AT"): "Austrian German",
    ("de", "CH"): "Swiss Standard German",
    ("es", "MX"): "Mexican Spanish",
    ("es", "ES"): "Castilian Spanish, as spoken in Spain",
    ("es", "AR"): "Rioplatense Spanish, as spoken in Argentina",
    ("es", "CO"): "Colombian Spanish",
    ("es", "US"): "US Latino Spanish",
    ("fr", "FR"): "standard French, as spoken in France",
    ("fr", "CA"): "Quebec French",
    ("fr", "BE"): "Belgian French",
    ("fr", "CH"): "Swiss French",
    ("hi", "IN"): "standard Hindi, as spoken in North India",
    ("ja", "JP"): "standard Tokyo Japanese",
    ("ja", "KANSAI"): "Kansai Japanese (Osaka dialect)",
    ("ko", "KR"): "standard Seoul Korean",
    ("pt", "BR"): "Brazilian Portuguese",
    ("pt", "PT"): "European Portuguese, as spoken in Portugal",
    ("zh", "CN"): "standard Mandarin Chinese (Putonghua)",
    ("zh", "TW"): "Taiwan Mandarin",
    ("zh", "SG"): "Singapore Mandarin",
    ("zh", "HK"): "Cantonese, as spoken in Hong Kong",
}

# Regions that a UI locale carries but that don't name a variety: hatch-i18n
# canonicalizes every Arabic UI to `ar-AR`, which means Arabic, not Argentina.
NO_VARIETY_REGIONS = {("ar", "AR")}

# Catalog native voices have no locale field yet; read the region from the
# accent label until they do.
ACCENT_REGION = {
    "French Canadian": ("fr", "CA"),
}

# Writing systems that give a saved voice's preview language away on their
# own. Scripts shared by several languages are left untagged rather than
# guessed: Han alone (zh, kanji-only ja, Cantonese), Arabic script (ar, fa,
# ur), Devanagari (hi, mr), Bengali (bn, as), Cyrillic and Latin.
SCRIPT_LANGUAGES = (
    ("ja", re.compile(r"[぀-ヿ]")),
    ("ko", re.compile(r"[가-힯ᄀ-ᇿ]")),
    ("he", re.compile(r"[֐-׿]")),
    ("th", re.compile(r"[฀-๿]")),
    ("ta", re.compile(r"[஀-௿]")),
    ("te", re.compile(r"[ఀ-౿]")),
    ("kn", re.compile(r"[ಀ-೿]")),
)

MAX_HINT_CHARS = 120
GENDERS = ("F", "M")


class CastError(ValueError):
    """A request the cast rule cannot plan, reported as `ok: false`."""

    def __init__(self, code, message, **extra):
        super().__init__(message)
        self.code = code
        self.extra = extra


def parse_language(value):
    """`ja`, `ja-JP`, `pt_BR`, `zh-Hant-TW` -> (base, region or None)."""
    text = (value or "").strip().replace("_", "-")
    if not text:
        raise CastError("language_required", "pass --language with the script's language")
    parts = [p for p in text.split("-") if p]
    base = ALIASES.get(parts[0].lower(), parts[0].lower())
    rest = [p.upper() for p in parts[1:]]
    script = None
    if rest and rest[0] in ("HANS", "HANT", "LATN", "CYRL", "ARAB"):
        script = rest.pop(0)
    region = rest[0] if rest else None
    if region and region.isdigit():
        region = None  # es-419 and similar: no single country
    if region is None and base == "zh" and script in ("HANS", "HANT"):
        region = "CN" if script == "HANS" else "TW"
    if (base, region) in NO_VARIETY_REGIONS:
        region = None
    return base, region


def resolve_locale(language, locale=None, presentation_locale=None):
    """Pick the variety: explicit locale, then the language's own region, then
    the UI locale's region when it is the same language, then the default."""
    base, region = parse_language(language)
    if base not in LANGUAGES:
        raise CastError(
            "podcast_language_not_supported",
            f"podcast narration in '{base}' is not supported",
            supported=sorted(LANGUAGES),
        )
    if locale:
        loc_base, loc_region = parse_language(locale)
        if loc_base == base and loc_region:
            region = loc_region
    if not region and presentation_locale:
        ui_base, ui_region = parse_language(presentation_locale)
        if ui_base == base and ui_region:
            region = ui_region
    if not region:
        region = LANGUAGES[base][1]
    return base, region


def locale_tag(base, region):
    return f"{base}-{region}" if region else base


def variety_name(base, region):
    return VARIETY.get((base, region)) or VARIETY.get((base, None)) or LANGUAGES[base][0]


NEGATION = re.compile(r"\b(?:not|no|never|isn't|aren't|wasn't|without)\b(?:\s+(?:a|an|the|too|very|really))*\s+\w+")


def _text_gender(text):
    """F or M when English text names exactly one gender and doesn't negate
    one; otherwise None. Traits in other languages give None, so pass the
    gender explicitly with --gender."""
    lowered = (text or "").lower()
    if NEGATION.search(lowered):
        return None  # "not a woman", "no deep male voice": don't guess
    female = re.search(r"\b(female|woman|women|feminine|she|her|girl|lady|grandmother|mother)\b", lowered)
    male = re.search(r"\b(male|man|men|masculine|he|his|him|boy|gentleman|grandfather|father)\b", lowered)
    if female and not male:
        return "F"
    if male and not female:
        return "M"
    return None


def _text_age(text):
    match = re.search(r"\((?:[FMN]), ([^)]+)\)", text or "")
    if match:
        return match.group(1).strip().lower()
    match = re.search(r"\b(young adult|young|middle-aged|older|old|elderly|in (?:her|his) \w+)\b", (text or "").lower())
    return match.group(1) if match else None


_VARIETY_NAMES = sorted(((name.casefold(), key) for key, name in VARIETY.items()), key=lambda item: -len(item[0]))
_LANGUAGE_NAMES = sorted(((name.casefold(), base) for base, (name, _, _) in LANGUAGES.items()),
                         key=lambda item: -len(item[0]))
_SPEAKS = re.compile(r"\bspeaks\s+([^.;]+)", re.IGNORECASE)
_LEARNER_ACCENT = re.compile(r"\bwith (?:a|an|some|slight|light|noticeable|strong)\b[^,.;]*\baccent\b", re.IGNORECASE)


def description_language(text):
    """(base, region) from a design description's "Speaks <variety>" sentence,
    which every podcast host brief starts with and the rewriter keeps. A voice
    that speaks the language with a foreign accent isn't a native match."""
    match = _SPEAKS.search(text or "")
    if not match:
        return None, None
    phrase = match.group(1).strip().casefold()
    if _LEARNER_ACCENT.search(phrase):
        return None, None
    for name, (base, region) in _VARIETY_NAMES:
        if phrase.startswith(name):
            return base, region
    phrase = re.sub(r"^(?:standard|native|fluent)\s+", "", phrase)
    for name, base in _LANGUAGE_NAMES:
        if phrase.startswith(name):
            return base, None
    return None, None


def script_language(text):
    """The language a preview line's writing system gives away, if any."""
    for base, pattern in SCRIPT_LANGUAGES:
        if pattern.search(text or ""):
            return base
    return None


class Voice:
    """A catalog or saved voice as the rule sees it."""

    def __init__(self, voice_id, *, kind, name=None, base=None, region=None, gender=None, age=None,
                 tone=None, description="", origin=None, saved_voice_id=None, score=0.0,
                 language_inferred=False, order=0, accent=None):
        self.voice_id = voice_id
        self.name = name
        self.kind = kind
        self.base = base
        self.region = region
        self.gender = gender
        self.age = age
        self.tone = tone
        self.description = description
        self.origin = origin
        self.saved_voice_id = saved_voice_id
        self.score = score
        self.language_inferred = language_inferred
        self.order = order
        self.accent = accent

    def native_for(self, base, region):
        """Native to the variety. A voice with no region is a weak match: it
        counts only for the language's default variety, so an untagged or
        MSA (`ar`) voice is never reused for Egyptian Arabic or Kansai."""
        if self.base != base:
            return False
        if self.region is None:
            return region is None or region == LANGUAGES.get(base, (None, None))[1]
        return self.region == region

    def same_language(self, base):
        return self.base == base


def load_catalog(path, shortlist_path=None):
    """Catalog voices, with shortlist voices first in shortlist order."""
    raw = json.loads(Path(path).read_text(encoding="utf-8")) if path and Path(path).is_file() else []
    shortlist = []
    if shortlist_path and Path(shortlist_path).is_file():
        shortlist = [v["id"] for v in json.loads(Path(shortlist_path).read_text(encoding="utf-8"))]
    voices = []
    for index, entry in enumerate(raw):
        iso3 = (entry.get("language") or "eng").lower()
        base = ISO3_TO_BASE.get(iso3)
        region = None
        locale = entry.get("locale")
        if locale:
            base, region = parse_language(locale)
        elif entry.get("accent") in ACCENT_REGION and ACCENT_REGION[entry["accent"]][0] == base:
            region = ACCENT_REGION[entry["accent"]][1]
        voices.append(Voice(
            entry["id"],
            kind="catalog",
            name=entry.get("name"),
            base=base,
            region=region,
            gender=entry.get("gender") if entry.get("gender") in GENDERS else None,
            age=_text_age(entry.get("long_description", "")),
            tone=entry.get("tone"),
            description=entry.get("long_description") or entry.get("description") or "",
            score=float(entry.get("aesthetics_mean") or 0.0),
            order=shortlist.index(entry["id"]) if entry["id"] in shortlist else len(shortlist) + index,
            accent=entry.get("accent"),
        ))
    return voices


def load_saved(path):
    """Saved voices from `~/user/voices.json`; a missing file means none."""
    if not path or not Path(path).is_file():
        return []
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    voices = []
    for index, entry in enumerate(raw if isinstance(raw, list) else []):
        voice_id = entry.get("voice_id")
        if not voice_id:
            continue
        base = region = None
        inferred = False
        if entry.get("language"):
            base, region = parse_language(entry["language"])
        else:
            # voice.design saves no language yet: read the brief's first
            # sentence, then a preview script only one language uses.
            base, region = description_language(entry.get("description", ""))
            if base is None:
                previews = " ".join(p.get("preview_text", "") for p in entry.get("profiles", []))
                base = script_language(previews)
            inferred = base is not None
        description = entry.get("description", "")
        gender = entry.get("gender") if entry.get("gender") in GENDERS else _text_gender(description)
        voices.append(Voice(
            voice_id,
            kind="saved",
            name=entry.get("voice_name"),
            base=base,
            region=region,
            gender=gender,
            age=_text_age(description),
            description=description,
            origin=entry.get("origin"),
            saved_voice_id=entry.get("saved_voice_id"),
            language_inferred=inferred,
            order=-index,  # newest (last) first
        ))
    return voices


def load_current(path, saved, catalog):
    """Muse's voice from `~/user/voice.json`, resolved to a Voice, or None."""
    if not path or not Path(path).is_file():
        return None
    selection = json.loads(Path(path).read_text(encoding="utf-8"))
    saved_id = (selection.get("saved_voice_id") or "").strip()
    if saved_id:
        match = [v for v in saved if v.saved_voice_id == saved_id]
        if not match:
            raise CastError("current_voice_unresolved", "the current saved voice is not in ~/user/voices.json")
        return match[0]
    voice_id = (selection.get("voice_id") or "").strip()
    if not voice_id:
        return None
    for voice in catalog + saved:
        if voice.voice_id == voice_id:
            return voice
    return Voice(voice_id, kind="unknown")


def clean_hint(text, limit=MAX_HINT_CHARS):
    """A short, single-line content hint for a brief."""
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]

def load_styles(path):
    """The native-speech descriptions (``references/podcast_native_styles.json``): a text per locale
    tag and a template for the others. A missing file means no styles."""
    if not path or not Path(path).is_file():
        return {}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {"template": raw.get("template"), "locales": dict(raw.get("locales") or {})}


def style_text(base, region, styles):
    """The description asking a voice to speak this variety like a native speaker, or None for
    English or when there are no styles."""
    if base == "en" or not styles:
        return None
    text = (styles.get("locales") or {}).get(locale_tag(base, region))
    if text:
        return text
    template = styles.get("template")
    if not template:
        return None
    return template.format(variety=variety_name(base, region), language=LANGUAGES[base][0])


def needs_style(voice, base):
    """A known voice that doesn't speak the language: any voice of another language. A voice of
    another variety of the same language already speaks it natively, and an unknown voice is left
    alone."""
    return base != "en" and voice is not None and voice.kind != "unknown" and not voice.same_language(base)


def _default_voice(voice):
    """A voice the skill picks when nobody chose one: the American English library voices."""
    return voice.kind == "catalog" and voice.base == "en" and (voice.accent or "American") == "American"


def load_varieties(path, catalog):
    """English region -> (accent label, variety name, its listed library voices in catalog order), from
    ``references/podcast_english_varieties.json``. A listed voice missing from the catalog is skipped."""
    if not path or not Path(path).is_file():
        return {}
    by_id = {v.voice_id: v for v in catalog}
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {region: (entry["accent"], entry.get("variety") or f"{entry['accent']} English",
                     [by_id[v["id"]] for v in entry.get("voices", []) if v.get("id") in by_id])
            for region, entry in raw.items()}


def _accent_voices(accent, varieties, catalog, used):
    """Free English library voices with this accent: the listed voices of the variety that has it, or,
    for an accent no variety lists (Scottish, Southern American), every catalog voice with exactly
    that accent label. Catalog order."""
    listed = next((voices for label, _, voices in varieties.values() if label.casefold() == accent.casefold()), None)
    if listed is None:
        listed = sorted((v for v in catalog if v.base == "en" and (v.accent or "").casefold() == accent.casefold()),
                        key=lambda v: v.order)
    return [v for v in listed if v.voice_id not in used]


# Short forms people use for an accent, as the library's labels. The two-letter ones count only in capitals
# ("US", not the word "us").
_ACCENT_ABBREVIATIONS = {"US": "american", "USA": "american", "UK": "british", "NZ": "new zealand",
                         "SA": "south african"}
_ACCENT_ALIASES = {"america": "american", "britain": "british", "brit": "british", "england": "british",
                   "english accent": "british accent", "kiwi": "new zealand", "south africa": "south african",
                   "aussie": "australian", "australia": "australian", "scotland": "scottish", "scots": "scottish",
                   "ireland": "irish", "india": "indian", "singapore": "singaporean", "singlish": "singaporean",
                   "canada": "canadian", "jamaica": "jamaican", "nigeria": "nigerian", "kenya": "kenyan",
                   "philippines": "filipino", "malaysia": "malaysian", "zimbabwe": "zimbabwean",
                   "trinidad": "trinidadian"}
# Words that describe an accent without naming one ("a light accent", "British English").
_ACCENT_FILLER = {"a", "an", "the", "accent", "accents", "accented", "voice", "with", "and", "or", "of", "in",
                  "light", "slight", "mild", "soft", "strong", "heavy", "thick", "noticeable", "some", "bit",
                  "little", "very", "posh", "drawl", "english", "native", "sounding", "like", "speaker"}


def _accent_words(text):
    """The words of an accent label or request, short forms and place names spelled as the library's labels
    ("a US accent" -> a american accent). Whole words only, so "US" never matches inside "Russian"."""
    text = text or ""
    for dotted, plain in (("U.S.A.", "USA"), ("U.S.", "US"), ("U.K.", "UK")):
        text = text.replace(dotted, plain)
    words = re.findall(r"[^\W\d_]+(?:-[^\W\d_]+)*", text)
    phrase = " " + " ".join(_ACCENT_ABBREVIATIONS.get(w, w.casefold()) for w in words) + " "
    for alias, label in _ACCENT_ALIASES.items():
        phrase = phrase.replace(f" {alias} ", f" {label} ")
    return phrase.split()


def _accent_matches(label, wanted):
    """Whether the request names this accent label: every word of the label is a word of the request
    ("Southern American" in "a southern American drawl"), or every naming word of the request is a word of
    the label ("southern" for "Southern American")."""
    label_words, wanted_words = set(_accent_words(label)), set(_accent_words(wanted))
    naming = wanted_words - _ACCENT_FILLER
    return bool(label_words) and (label_words <= wanted_words or bool(naming) and naming <= label_words)


def _library_accent(accent, catalog):
    """The library's label for the accent the user asked for ("British" for "a British accent" or "UK"), else
    None. The label the request names exactly, then the longest label all of whose words it has ("Southern
    American" over "American"), then the shortest label that has all its naming words. Words match whole, so
    "US" means American, never Russian or Australian. An accent no library voice has (a variety of the
    episode's own language such as "québécois", "Asian", or a typo) can't be honoured with an accented voice,
    so the host is cast as if none was asked."""
    if not accent:
        return None
    labels = {v.accent for v in catalog if v.base == "en" and _accent_matches(v.accent, accent)}
    naming = set(_accent_words(accent)) - _ACCENT_FILLER

    def rank(label):
        words = set(_accent_words(label))
        if words == naming:
            return 0, 0, label
        if words <= naming:
            return 1, -len(words), label
        return 2, len(words), label

    return min(labels, key=rank) if labels else None


def resolve_voice_name(value, catalog, saved):
    """A voice ID as given, or the one voice whose display name matches it
    (`Aria` -> `avocado_v2:MAI_01`). Ambiguous or unknown names stay as given
    for tts-cli's own validation to report."""
    if any(v.voice_id == value for v in saved + catalog):
        return value
    wanted = value.strip().casefold()
    matches = {v.voice_id for v in saved + catalog if (v.name or "").casefold() == wanted}
    return matches.pop() if len(matches) == 1 else value


def _find(voice_id, catalog, saved):
    for voice in saved + catalog:
        if voice.voice_id == voice_id:
            return voice
    return None


def _best(voices, base, region, gender, used, prefer_origin=None):
    """The best unused native voice. When the host has a gender, only a voice
    known to have that gender fills it: saved designs carry no gender field,
    and an unknown one can put a woman's voice on "grandpa". Those hosts get
    a fallback or styled voice instead."""
    pool = [
        v for v in voices
        if v.native_for(base, region) and v.voice_id not in used
        and (gender is None or v.gender == gender)
    ]
    if not pool:
        return None
    return sorted(
        pool,
        key=lambda v: (
            v.region != region,  # an exact variety beats a weak, region-less match
            gender is not None and v.gender is None,
            prefer_origin is not None and v.origin != prefer_origin,
            -v.score,
            v.order,
        ),
    )[0]


def plan_cast(*, language, hosts, catalog, saved, current=None, locale=None,
              presentation_locale=None, voices=None, series=None, traits=None,
              genders=None, host_languages=None, accents=None, new_voices=False, styles=None,
              varieties=None):
    """Plan every host. `hosts` is the ordered host names (main host first);
    the other mappings go from a host name to a value. `styles` holds the
    native-speech descriptions (`load_styles`), `varieties` maps an English
    region to its accent and voices (`load_varieties`)."""
    voices = voices or {}
    series = series or {}
    traits = traits or {}
    genders = genders or {}
    host_languages = host_languages or {}
    accents = accents or {}
    varieties = varieties or {}
    if not hosts:
        raise CastError("hosts_required", "pass at least one --host")
    if len(set(hosts)) != len(hosts):
        raise CastError("duplicate_host", "host names must differ")
    for name, gender in genders.items():
        if gender not in GENDERS:
            raise CastError("bad_argument", f"--gender for {name} must be F or M")
    base, region = resolve_locale(language, locale, presentation_locale)
    result = {
        "ok": True,
        "language": base,
        "locale": locale_tag(base, region),
        "variety": variety_name(base, region),
    }
    host_locales = {}
    for name in hosts:
        if host_languages.get(name):
            host_locales[name] = resolve_locale(host_languages[name], None, None)
        else:
            host_locales[name] = (base, region)
    # English hosts with an accent the request names: --accent for the host, else the region its
    # language names (in --language, --locale or --host-language; never the UI locale alone).
    named_region = None
    lang_base, lang_region = parse_language(language)
    if lang_base == "en":
        named_region = lang_region
        if locale and parse_language(locale)[0] == "en" and parse_language(locale)[1]:
            named_region = parse_language(locale)[1]
    english_accent = {}
    for name in hosts:
        if host_locales[name][0] != "en":
            continue
        asked = _library_accent(accents.get(name), catalog)
        own = parse_language(host_languages[name])[1] if host_languages.get(name) else named_region
        if asked:
            english_accent[name] = asked
        elif own in varieties:
            english_accent[name] = varieties[own][0]
    if all(host_locales[n][0] == "en" for n in hosts) and not english_accent:
        result["use_existing_rules"] = True
        return result
    if base == "en" and named_region in varieties:
        result["variety"] = varieties[named_region][1]

    used = set()
    planned = []

    # First pass: voices the user named, then series voices. A voice the user
    # asked for on this host beats the series' voice for it.
    for name in hosts:
        entry = {"name": name, "language": locale_tag(*host_locales[name])}
        explicit = voices.get(name)
        if explicit:
            if explicit == "current":
                if current is None:
                    raise CastError("current_voice_unresolved", "Muse has no current voice to use")
                entry.update(source="user", voice_id=current.voice_id)
            else:
                entry.update(source="user", voice_id=resolve_voice_name(explicit, catalog, saved))
            if series.get(name) and series[name] != entry["voice_id"]:
                entry["note"] = "replaces the series voice for this host at the user's request"
            voice = _find(entry["voice_id"], catalog, saved)
            if voice is None or not voice.native_for(*host_locales[name]):
                entry["note"] = (entry.get("note", "") + "; " if entry.get("note") else "") + \
                    "user-chosen voice is not native to the language; honour it"
            used.add(entry["voice_id"])
        elif series.get(name):
            entry.update(source="series", voice_id=series[name])
            used.add(series[name])
        planned.append(entry)

    current_taken = current is not None and current.voice_id in used
    known = [(_find(e.get("voice_id"), catalog, saved) or Voice("", kind="unknown")).gender
             if e.get("voice_id") else None for e in planned]

    def candidates_for(pool, gender):
        """Up to 8 voice IDs from `pool` (free voices only), the planned gender first."""
        return [v.voice_id for v in sorted(
            pool, key=lambda v: (gender is not None and v.gender != gender, -v.score, v.order))[:8]]

    for index, entry in enumerate(planned):
        if "source" in entry:
            continue
        name = entry["name"]
        hbase, hregion = host_locales[name]
        trait = traits.get(name)
        accent = _library_accent(accents.get(name), catalog)
        described = bool(trait or accent)
        gender = genders.get(name)
        gender_source = "user" if gender else None
        if gender is None and trait:
            gender = _text_gender(trait)
            gender_source = "traits" if gender else "unspecified"
        twin = None
        if index == 0 and current is not None and not current_taken and not described:
            twin = current
        if gender is None and not trait:
            if twin is not None and twin.gender:
                gender, gender_source = twin.gender, "muse_voice"
            else:
                taken = [g for i, g in enumerate(known) if g and i != index]
                gender = ("M" if taken[-1] == "F" else "F") if taken else ("M" if index > 0 else "F")
                gender_source = "contrast"
        entry["gender"] = gender
        entry["gender_source"] = gender_source
        if accents.get(name):
            entry["accent"] = clean_hint(accents[name])
        known[index] = gender

        # An English host with a named variety or accent gets a library voice with that accent:
        # Muse's own voice when it has it, else the variety's voices (candidates for a described
        # host). With none of the planned gender left, today's English choice below.
        wanted = english_accent.get(name)
        if hbase == "en" and wanted:
            entry["accent"] = wanted
            pool = _accent_voices(wanted, varieties, catalog, used)
            if trait and pool:
                candidates = candidates_for(pool, gender)
                entry.update(source="variety", voice_id=None, candidates=candidates, start_voice_id=candidates[0],
                             note="choose the candidate whose description fits the user's traits")
                used.add(candidates[0])
                continue
            if (index == 0 and current is not None and not current_taken and not trait and not new_voices
                    and (current.accent or "").casefold() == wanted.casefold()):
                entry.update(source="current", voice_id=current.voice_id)
                used.add(current.voice_id)
                current_taken = True
                known[index] = current.gender
                continue
            pick = next((v for v in pool if gender is None or v.gender == gender), None)
            if pick is not None:
                entry.update(source="variety", voice_id=pick.voice_id)
                used.add(pick.voice_id)
                known[index] = pick.gender
                continue

        # An English host in a bilingual show keeps today's English choices.
        if hbase == "en" and (wanted or not described):
            if index == 0 and current is not None and not current_taken:
                entry.update(source="current", voice_id=current.voice_id)
                used.add(current.voice_id)
                current_taken = True
            else:
                pick = next((v for v in sorted(catalog, key=lambda v: v.order)
                             if v.base == "en" and v.voice_id not in used and v.gender in (gender, None)), None)
                entry.update(source="library", voice_id=pick.voice_id if pick else None)
                if pick:
                    used.add(pick.voice_id)
            known[index] = (_find(entry.get("voice_id"), catalog, saved) or Voice("", kind="unknown")).gender
            continue

        if not described and not new_voices and twin is not None and current.native_for(hbase, hregion):
            entry.update(source="current", voice_id=current.voice_id)
            used.add(current.voice_id)
            current_taken = True
            known[index] = current.gender
            continue
        if not described and not new_voices:
            pick = _best(saved, hbase, hregion, gender, used, prefer_origin="podcast_auto")
            if pick is not None:
                entry.update(source="saved", voice_id=pick.voice_id, saved_voice_id=pick.saved_voice_id)
                if pick.language_inferred:
                    entry["language_inferred"] = True
                used.add(pick.voice_id)
                known[index] = pick.gender
                continue
        library = [v for v in catalog if v.native_for(hbase, hregion) and v.voice_id not in used]
        if library and not described and not new_voices:
            pick = _best(library, hbase, hregion, gender, used)
            if pick is not None:
                entry.update(source="library", voice_id=pick.voice_id)
                used.add(pick.voice_id)
                known[index] = pick.gender
                continue
        # A described host chooses among the native library voices, or else among the
        # American English library voices, which then get the style. The first candidate is
        # free (the pool leaves out voices other hosts hold); it is reserved as this host's
        # starting voice so no two hosts start on the same one.
        # The same order as for a host nobody described: native voices of another variety of the
        # language (Canadian French for French) come before the styled voices.
        pool, source = library, "library"
        if not pool:
            pool, source = [v for v in catalog if v.same_language(hbase) and v.voice_id not in used], "fallback"
        if not pool:
            pool, source = [v for v in catalog if _default_voice(v) and v.voice_id not in used], "styled"
        if pool and trait and not accent:
            candidates = candidates_for(pool, gender)
            entry.update(
                source=source,
                voice_id=None,
                candidates=candidates,
                start_voice_id=candidates[0],
                note="choose the candidate whose description fits the user's traits",
            )
            used.add(candidates[0])
            continue
        entry.update(source="fallback", voice_id=None)

    def closest(index, entry):
        """(voice_id, source) for a host no rule above filled: a library voice with
        the accent the user asked for, else a native voice of another variety of
        the language (`fallback`); then the skill's usual voices (`styled`): Muse's
        voice for the main host, then the shortlist, then the other American
        English voices. The planned gender where one was planned."""
        hbase = host_locales[entry["name"]][0]
        gender = entry.get("gender")
        accent = _library_accent(accents.get(entry["name"]), catalog)
        ordered = sorted(catalog, key=lambda v: v.order)

        def fits(voice, strict=False):
            if voice.voice_id in used:
                return False
            return gender is None or voice.gender == gender or (not strict and voice.gender is None)

        if accent:
            for exact in (True, False):
                for voice in sorted(catalog, key=lambda v: (-v.score, v.order)):
                    label = (voice.accent or "").casefold()
                    if voice.base == "en" and fits(voice, strict=True) and (
                            label == accent.casefold().strip() if exact else _accent_matches(voice.accent, accent)):
                        return voice.voice_id, "fallback"
        else:
            for voice in ordered:
                if voice.same_language(hbase) and fits(voice):
                    return voice.voice_id, "fallback"
        if index == 0 and current is not None and fits(current):
            return current.voice_id, "fallback" if current.same_language(hbase) else "styled"
        for strict in (True, False):
            for voice in ordered:
                if _default_voice(voice) and fits(voice, strict=strict):
                    return voice.voice_id, "styled"
        return None, "fallback"

    for index, entry in enumerate(planned):
        if entry.get("source") == "fallback" and not entry.get("candidates"):
            entry["voice_id"], entry["source"] = closest(index, entry)
            if entry["voice_id"]:
                used.add(entry["voice_id"])

    # Native speech for every host whose voice doesn't speak the episode's language. generate
    # works the styles out again from its --language and voices, so the hosts it must leave
    # alone are listed in `no_style`: a host the user gave an accent, and a host speaking
    # another language than the episode's (the English host of a bilingual show).
    no_style = []
    for entry in planned:
        hbase, hregion = host_locales[entry["name"]]
        voice = _find(entry.get("voice_id") or entry.get("start_voice_id"), catalog, saved)
        accented_host = bool(_library_accent(accents.get(entry["name"]), catalog))
        other_language = (hbase, hregion) != (base, region)
        if needs_style(voice, hbase) and not accented_host and not other_language:
            text = style_text(hbase, hregion, styles)
            if text:
                entry["style"] = text
        elif needs_style(voice, base) and (accented_host or other_language):
            no_style.append(entry["name"])

    result["hosts"] = planned
    if any(e["source"] == "fallback" and "style" not in e and host_locales[e["name"]][0] != "en" for e in planned):
        result["note"] = "non-English audio with these voices may sound a little accented; tell the user once"
    # Ready-to-run steps, so the agent follows the plan instead of re-deriving it:
    # `speakers` are generate's --speaker values for every host (a host picked by
    # traits starts on its first candidate), and `choose` lists those hosts'
    # candidates with their descriptions so the agent can swap in the one that fits.
    choices = [e for e in planned if e.get("candidates") and not e.get("voice_id")]
    described_by_id = {v.voice_id: v.description for v in catalog}
    result["speakers"] = [f"{e['name']}={e.get('voice_id') or e['start_voice_id']}"
                          for e in planned if e.get("voice_id") or e.get("start_voice_id")]
    if no_style:
        result["no_style"] = no_style
    if choices:
        result["choose"] = [{"name": e["name"], "traits": traits.get(e["name"]),
                             "candidates": [{"voice_id": c, "description": _short(described_by_id.get(c, ""))}
                                            for c in e["candidates"]]} for e in choices]
    return result


def _short(text, limit=160):
    """A catalog description cut at a word boundary, for the plan's `choose` entries."""
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "..."


REFUSED_FILENAME = ".refused_voices.json"
# A refusal is forgotten after this long, so one bad day never drops a saved voice for good.
REFUSED_TTL_SECONDS = 30 * 24 * 3600


def refused_voice_from_error(text):
    """The saved voice tts-cli reports the podcast voice service refused as unknown: the
    `refused_voice_id` of a JSON line on its stderr, or None. tts-cli writes that line only for
    `ctts_unknown_voice` on a saved design's turn, so an error that may come from the turn
    (`invalid_params`) or any change to the error's wording never records a voice."""
    for line in (text or "").splitlines():
        line = line.strip()
        if not (line.startswith("{") and "refused_voice_id" in line):
            continue
        try:
            report = json.loads(line)
        except ValueError:
            continue
        if isinstance(report, dict) and isinstance(report.get("refused_voice_id"), str) and report["refused_voice_id"]:
            return report["refused_voice_id"]
    return None


def saved_voice_fingerprint(saved_path, voice_id):
    """A hash of the saved record for this voice in ~/user/voices.json, or None when it can't be read.
    A refusal holds only while the record is unchanged: a new design under the same voice is cast again."""
    try:
        records = json.loads(Path(saved_path).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    record = next((r for r in records if isinstance(r, dict) and r.get("voice_id") == voice_id), None) \
        if isinstance(records, list) else None
    if record is None:
        return None
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def _refused_entries(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("voice_id")] if isinstance(data, list) else []


def load_refused(path, saved_path=None, now=None):
    """Voice IDs the podcast voice service refused in the last 30 days (podcast-helper generate records
    them), leaving out any whose saved record changed since."""
    now = time.time() if now is None else now
    refused = set()
    for entry in _refused_entries(path):
        at = entry.get("refused_at")
        if not isinstance(at, (int, float)) or now - at > REFUSED_TTL_SECONDS:
            continue
        if saved_path is not None and entry.get("fingerprint") is not None and \
                saved_voice_fingerprint(saved_path, entry["voice_id"]) != entry["fingerprint"]:
            continue
        refused.add(str(entry["voice_id"]))
    return refused


def record_refused(path, voice_id, saved_path=None, now=None):
    """Remember one refused voice, with when and its saved record's fingerprint, so plans for the next 30
    days skip it while that record is unchanged. Expired entries are dropped. Never raises."""
    if not voice_id:
        return
    now = time.time() if now is None else now
    try:
        path = Path(path)
        kept = [e for e in _refused_entries(path)
                if e["voice_id"] != voice_id and isinstance(e.get("refused_at"), (int, float))
                and now - e["refused_at"] <= REFUSED_TTL_SECONDS]
        kept.append({"voice_id": voice_id, "refused_at": int(now),
                     "fingerprint": saved_voice_fingerprint(saved_path, voice_id) if saved_path else None})
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(kept), encoding="utf-8")
    except OSError:
        pass


def default_paths():
    home = Path(os.environ.get("JARVIS_HOME", os.path.expanduser("~")))
    assets = Path(os.environ.get("MUSE_VOICE_SELECTOR_DIR", "/opt/muse/assets/voice-selector"))
    skill = Path(__file__).resolve().parent.parent
    return {
        "catalog": assets / "voice_source.json",
        "shortlist": skill / "references" / "podcast_preferred_voices.json",
        "styles": skill / "references" / "podcast_native_styles.json",
        "varieties": skill / "references" / "podcast_english_varieties.json",
        "saved": home / "user" / "voices.json",
        "current": home / "user" / "voice.json",
        "refused": home / "workspace" / "podcasts" / REFUSED_FILENAME,
    }


def parse_mapping(values, flag):
    mapping = {}
    for value in values or []:
        if "=" not in value:
            raise CastError("bad_argument", f"{flag} takes NAME=VALUE, got {value!r}")
        name, _, rest = value.partition("=")
        name, rest = name.strip(), rest.strip()
        if not name or not rest:
            raise CastError("bad_argument", f"{flag} takes NAME=VALUE, got {value!r}")
        mapping[name] = rest
    return mapping


def cmd_cast(args):
    """Entry point for `podcast-helper cast`; prints the plan as JSON."""
    paths = default_paths()
    try:
        catalog = load_catalog(paths["catalog"], paths["shortlist"])
        saved = load_saved(paths["saved"])
        # Voices the podcast voice service refused (recorded by generate, or
        # named with --exclude-voice) are never picked automatically. A voice
        # the user names with --voice still goes through as their choice.
        excluded = set(getattr(args, "exclude_voice", None) or []) | load_refused(paths["refused"],
                                                                                   paths["saved"])
        # Muse's own voice is looked up before the refused voices are dropped, so a refused saved
        # voice of hers only leaves her voice out of the plan instead of failing every later cast.
        current = load_current(paths["current"], saved, catalog)
        if current is not None and current.voice_id in excluded:
            current = None
        saved = [v for v in saved if v.voice_id not in excluded]
        catalog = [v for v in catalog if v.voice_id not in excluded]
        plan = plan_cast(
            language=args.language,
            locale=args.locale,
            presentation_locale=os.environ.get("JARVIS_PRESENTATION_LOCALE"),
            hosts=args.host,
            catalog=catalog,
            saved=saved,
            current=current,
            voices=parse_mapping(args.voice, "--voice"),
            series=parse_mapping(args.series_voice, "--series-voice"),
            traits=parse_mapping(args.traits, "--traits"),
            genders={k: v.upper() for k, v in parse_mapping(args.gender, "--gender").items()},
            host_languages=parse_mapping(args.host_language, "--host-language"),
            accents=parse_mapping(args.accent, "--accent"),
            new_voices=args.new_voices,
            styles=load_styles(paths["styles"]),
            varieties=load_varieties(paths["varieties"], catalog),
        )
        if excluded:
            plan["excluded_voices"] = sorted(excluded)
    except CastError as error:
        plan = {"ok": False, "error": error.code, "message": str(error), **error.extra}
    print(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))
    return plan


def speaker_styles(language, speakers, no_style=(), paths=None):
    """generate's `--speaker-description` values: NAME=TEXT for each NAME=VOICE_ID speaker whose voice
    doesn't speak the episode's language, except the hosts in `no_style`. Errors leave the episode
    unstyled rather than failing it."""
    paths = paths or default_paths()
    try:
        base, region = resolve_locale(language, None, None)
        styles = load_styles(paths["styles"])
        if base == "en" or not styles:
            return []
        catalog = load_catalog(paths["catalog"], paths["shortlist"])
        saved = load_saved(paths["saved"])
    except (CastError, OSError, ValueError):
        return []
    skip = set(no_style or [])
    text = style_text(base, region, styles)
    out = []
    for mapping in speakers or []:
        name, _, voice_id = mapping.partition("=")
        name, voice_id = name.strip(), voice_id.strip()
        if not name or not voice_id or name in skip:
            continue
        if text and needs_style(_find(voice_id, catalog, saved), base):
            out.append(f"{name}={text}")
    return out


def add_cast_parser(subparsers):
    sp = subparsers.add_parser(
        "cast",
        help="Choose native-language host voices for a non-English episode",
    )
    sp.add_argument("--language", required=True, help="Narration language, such as ja, pt_BR or fr-CA")
    sp.add_argument("--locale", help="Variety when the user asked for one, such as pt-PT or ja-KANSAI")
    sp.add_argument("--host", action="append", required=True,
                    help="Host or character name, main voice first (repeat, one per speaking character)")
    sp.add_argument("--voice", action="append", metavar="NAME=VOICE_ID",
                    help="A voice the user chose for this host; VOICE_ID 'current' is Muse's voice")
    sp.add_argument("--series-voice", action="append", metavar="NAME=VOICE_ID",
                    help="The series' established voice for this host")
    sp.add_argument("--traits", action="append", metavar="NAME=TEXT",
                    help="Voice traits the user described for this host")
    sp.add_argument("--gender", action="append", metavar="NAME=F|M",
                    help="The host's gender when the user gave or implied one, in any language")
    sp.add_argument("--host-language", action="append", metavar="NAME=LANG",
                    help="This host speaks another language, as in a bilingual show")
    sp.add_argument("--accent", action="append", metavar="NAME=ACCENT",
                    help="The user wants this host to speak with this accent, such as 'American'")
    sp.add_argument("--new-voices", action="store_true", help="The user asked for new voices: don't reuse saved ones")
    sp.add_argument("--exclude-voice", action="append", metavar="VOICE_ID",
                    help="A voice the podcast voice service refused: plan without it (repeat)")
    return sp
