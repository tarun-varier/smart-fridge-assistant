"""Category vocabulary & fuzzy matching for receipt line items (issue #4:
Category vocabulary & matching).

Fixed vocabulary {apple, banana, orange}, derived from the Vision Pipeline's
6-way fresh/rotten labels (see CONTEXT.md). A receipt line with no confident
match -- or a tie between two categories -- is flagged `unrecognized
category` rather than dropped or bucketed.
"""

import re

from rapidfuzz import fuzz, process

CATEGORY_SYNONYMS: dict[str, list[str]] = {
    "apple": ["apple", "apples", "fuji", "gala", "granny smith", "honeycrisp", "red delicious", "braeburn"],
    "banana": ["banana", "bananas", "plantain"],
    "orange": ["orange", "oranges", "navel orange", "valencia", "mandarin", "clementine", "tangerine"],
}

UNRECOGNIZED = "unrecognized category"

# Left as implementation-time tuning by issue #4. Below this score, a
# receipt line is flagged unrecognized rather than force-matched to the
# nearest category.
MATCH_THRESHOLD = 75

_STRIP_WORDS = {"organic", "fresh", "large", "small", "medium", "bag", "each", "lb", "lbs", "oz", "ct", "pk"}

_NAME_TO_CATEGORY = {name: category for category, names in CATEGORY_SYNONYMS.items() for name in names}
_ALL_NAMES = list(_NAME_TO_CATEGORY)


def normalize(line: str) -> str:
    """Lowercase; strip digits/currency/punctuation and common modifiers."""
    text = re.sub(r"[\$\d.,]+", " ", line.lower())
    words = [w for w in re.findall(r"[a-z]+", text) if w not in _STRIP_WORDS]
    return " ".join(words)


def match_category(line: str) -> str:
    """Fuzzy-match one receipt line against the fixed Category vocabulary.

    Returns the matched Category, or UNRECOGNIZED when no name clears
    MATCH_THRESHOLD or the top two candidates tie across different
    categories (an honest ambiguous match, not a coin flip).
    """
    normalized = normalize(line)
    if not normalized:
        return UNRECOGNIZED

    matches = process.extract(normalized, _ALL_NAMES, scorer=fuzz.token_set_ratio, limit=2)
    if not matches or matches[0][1] < MATCH_THRESHOLD:
        return UNRECOGNIZED

    top_name, top_score, _ = matches[0]
    if len(matches) > 1:
        runner_name, runner_score, _ = matches[1]
        if runner_score == top_score and _NAME_TO_CATEGORY[runner_name] != _NAME_TO_CATEGORY[top_name]:
            return UNRECOGNIZED

    return _NAME_TO_CATEGORY[top_name]
