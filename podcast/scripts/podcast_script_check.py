"""Check a podcast script before synthesis: its length and the format problems that would be spoken wrong.

`generate` runs this before rendering, so the agent can write the script once and go straight to
`generate` instead of counting words or re-reading the file in extra turns. A problem stops the render
and comes back as one line; a clean script renders, and the check rides along in the result.

The speaker-tag rules mirror tts-cli's parser (crates/tts-cli/src/chunking.rs `parse_turns`): a turn
starts on a line whose text, after leading whitespace, begins with a mapped name, a colon and a space.
Text before the first turn is dropped, and any other line, including an unmapped "Name: " line, is
spoken as part of the turn before it.
"""

import re
import unicodedata

# Spoken rates of the podcast voices, measured on real renders (11-19, cTTS and Shortwave, script
# counts over rendered audio length): English about 183 words a minute (n=13, 170-199), Japanese
# about 341 characters (n=8) and Korean about 327 (n=7). Scripts written without spaces between
# words are measured in characters. Chinese and Thai are typical speaking rates, not measured.
WORDS_PER_MINUTE = 180
CHARACTERS_PER_MINUTE = {"ja": 340, "zh": 290, "yue": 250, "ko": 325, "th": 400}
# Around a single target: 80% to 125%. Around a range: 90% of its low end to 110% of its high end.
SINGLE_TARGET_BAND = (0.8, 1.25)
RANGE_TARGET_BAND = (0.9, 1.1)

# A line that looks like "Name: ..." or "Name：...": up to three short words before the colon.
_TAG_LIKE = re.compile(r"^(?P<name>[^\s:：][^:：]{0,39}?)\s*(?P<colon>[:：])(?P<space>\s?)")
_MARKUP = (
    (re.compile(r"\[[^\]]*\]"), "square brackets"),
    (re.compile(r"\*\*|__"), "markdown emphasis"),
    (re.compile(r"^\s*#{1,6}\s"), "a markdown heading"),
    (re.compile(r"^\s*([-*_=])\1{2,}\s*$"), "a separator line"),
    (re.compile(r"https?://\S+"), "a link"),
)


def parse_speakers(mappings):
    """Speaker names from `Name=voice_id` mappings, in order."""
    names = []
    for mapping in mappings or []:
        name = mapping.split("=", 1)[0].strip()
        if name and name not in names:
            names.append(name)
    return names


def parse_target(text):
    """`--minutes` as (low, high) minutes: "6" or "5-8". None when absent."""
    if text is None or not str(text).strip():
        return None
    parts = re.split(r"\s*[-–]\s*", str(text).strip())
    try:
        values = [float(part) for part in parts]
    except ValueError:
        raise ValueError(f'--minutes must be a number of minutes or a range such as "5-8", not "{text}"')
    if len(values) not in (1, 2) or any(value <= 0 for value in values) or values[0] > values[-1]:
        raise ValueError(f'--minutes must be a number of minutes or a range such as "5-8", not "{text}"')
    return values[0], values[-1]


def _tag_name(line):
    """The name in a line that looks like a speaker tag, or None. A name is up to three words, each
    capitalized, or up to twelve characters of a script without case (such as Japanese)."""
    tag = _TAG_LIKE.match(line)
    if not tag:
        return None
    name = tag.group("name").strip()
    words = name.split()
    # A name starts with a letter: "7:30" is a time, not a tag.
    if len(words) > 3 or not name[0].isalpha():
        return None
    if all(word[0].isupper() for word in words):
        return name
    if not any(c.isupper() or c.islower() for c in name) and len(name) <= 12:
        return name
    return None


def _base_language(language):
    return re.split(r"[_-]", (language or "").strip().lower())[0]


# Emoji blocks only: pictographs, symbols and dingbats, and the arrows and stars block. Other
# symbols such as "㎡" or "㎞" are spoken as units and stay.
_EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF))


def _is_emoji(char):
    code = ord(char)
    return unicodedata.category(char) == "So" and any(low <= code <= high for low, high in _EMOJI_RANGES)


def measure(spoken_text, language):
    """(count, unit, minutes) for the text that will be spoken."""
    base = _base_language(language)
    words = len(spoken_text.split())
    letters = [c for c in spoken_text if c.isalnum()]
    # Mostly unspaced text (Japanese, Chinese, Thai) or a language measured by characters.
    unspaced = bool(letters) and words * 8 < len(letters)
    if base in CHARACTERS_PER_MINUTE or unspaced:
        rate = CHARACTERS_PER_MINUTE.get(base, 300)
        count = sum(1 for c in spoken_text if c.isalnum())
        return count, "characters", count / rate
    return words, "words", words / WORDS_PER_MINUTE


def check_script(script, speaker_mappings, language=None, minutes=None):
    """Measure the script and list what would be spoken wrong. Returns a dict with `ok`, `count`,
    `unit`, `minutes`, `target`, `problems` (these stop the render), `notes` (reported only) and
    `line` (the one-line report)."""
    names = parse_speakers(speaker_mappings)
    target = parse_target(minutes)
    problems = []
    spoken = []
    started = False
    leading = None
    used = set()
    unmapped = {}
    notes = []
    for number, raw in enumerate(script.splitlines(), start=1):
        line = raw.lstrip()
        speaker = next((name for name in names if line.startswith(f"{name}: ")), None)
        if speaker:
            started = True
            used.add(speaker)
            text = line[len(speaker) + 2:]
        else:
            text = line
            name = _tag_name(line)
            if name in names:
                problems.append(f'line {number}: write "{name}: " with an ASCII colon and a space')
            elif not started:
                if line.strip() and leading is None:
                    leading = number
            elif name:
                unmapped.setdefault(name, []).append(number)
        if not text.strip():
            continue
        if started:
            spoken.append(text)
        for pattern, what in _MARKUP:
            if pattern.search(text):
                problems.append(f"line {number}: {what} would be read aloud")
                break
        else:
            if any(_is_emoji(char) for char in text):
                problems.append(f"line {number}: an emoji would be read aloud or dropped")
    # An unmapped "Name: " on two or more lines is a missing --speaker (its lines would be spoken
    # by the host before them, name and all). Once is more likely an ordinary line such as
    # "Remember: ..." or "ポイント：...", so it is reported without stopping the render.
    mapped = ", ".join(names) or "none"
    for name, numbers in unmapped.items():
        where = "line " + str(numbers[0]) if len(numbers) == 1 else "lines " + ", ".join(map(str, numbers))
        if len(numbers) > 1:
            problems.append(f'{where}: "{name}" is not a --speaker (mapped: {mapped})')
        else:
            notes.append(f'{where}: "{name}:" is spoken as part of the turn before it')
    if leading is not None and started:
        problems.insert(0, f"line {leading}: text before the first speaker tag is not spoken")
    if not started:
        mapped = ", ".join(f'"{name}: "' for name in names) or "a mapped name"
        problems.insert(0, f"no line starts with a speaker tag such as {mapped}")

    count, unit, estimate = measure("\n".join(spoken), language)
    if target and started:
        low, high = target
        band = SINGLE_TARGET_BAND if low == high else RANGE_TARGET_BAND
        wanted = f"{_fmt(low)}" if low == high else f"{_fmt(low)}-{_fmt(high)}"
        # The length the target asks for, in the unit counted, so one rewrite lands in range.
        rate = WORDS_PER_MINUTE if unit == "words" else CHARACTERS_PER_MINUTE.get(_base_language(language), 300)
        aim = f"{round(low * rate, -1):.0f}" + ("" if low == high else f"-{round(high * rate, -1):.0f}")
        if estimate < low * band[0]:
            problems.append(f"under the {wanted}-minute target (about {aim} {unit})")
        elif estimate > high * band[1]:
            problems.append(f"over the {wanted}-minute target (about {aim} {unit})")

    unused = [name for name in names if name not in used]
    summary = f"{count} {unit}, about {estimate:.1f} minutes"
    if target:
        summary += f" (target {_fmt(target[0])}" + (f"-{_fmt(target[1])}" if target[1] != target[0] else "") + ")"
    if problems:
        # Repeated problems of one kind are summarized so the line stays short.
        shown = problems[:6]
        more = f"; and {len(problems) - 6} more" if len(problems) > 6 else ""
        line = f"script check: {summary}; fix: " + "; ".join(shown) + more
    else:
        line = f"script check: {summary}; OK"
    if notes:
        line += "; note: " + "; ".join(notes[:3]) + (f"; and {len(notes) - 3} more" if len(notes) > 3 else "")
    return {
        "ok": not problems,
        "count": count,
        "unit": unit,
        "minutes": round(estimate, 1),
        "target": list(target) if target else None,
        "problems": problems,
        "notes": notes,
        "unused_speakers": unused,
        "line": line,
    }


def _fmt(value):
    return f"{value:g}"
