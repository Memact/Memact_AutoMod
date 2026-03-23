from __future__ import annotations

from collections.abc import Iterable
import json
import re
from urllib.request import Request, urlopen


DATASET_PRESETS = {
    "ldnoobw_en": {
        "label": "LDNOOBW English",
        "urls": [
            "https://raw.githubusercontent.com/LDNOOBW/naughty-words-js/master/en.json",
        ],
    },
    "ldnoobw_hi": {
        "label": "LDNOOBW Hindi",
        "urls": [
            "https://raw.githubusercontent.com/LDNOOBW/naughty-words-js/master/hi.json",
        ],
    },
    "ldnoobw_en_hi": {
        "label": "LDNOOBW English + Hindi",
        "urls": [
            "https://raw.githubusercontent.com/LDNOOBW/naughty-words-js/master/en.json",
            "https://raw.githubusercontent.com/LDNOOBW/naughty-words-js/master/hi.json",
        ],
    },
}

SIMPLE_TERM_RE = re.compile(r"^[\w'-]+$", re.UNICODE)


def normalize_blocked_term(term: str) -> str | None:
    normalized = " ".join(term.strip().casefold().split())
    if not normalized:
        return None
    if normalized.startswith("#") or normalized.startswith("//"):
        return None
    if len(normalized) > 80:
        return None
    return normalized


def normalize_blocked_terms(terms: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    normalized_terms: list[str] = []
    for term in terms:
        normalized = normalize_blocked_term(term)
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        normalized_terms.append(normalized)
    return normalized_terms


def compile_blocked_term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    if SIMPLE_TERM_RE.fullmatch(term):
        return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def fetch_dataset_terms_sync(preset: str) -> list[str]:
    dataset = DATASET_PRESETS.get(preset)
    if dataset is None:
        raise ValueError("Unknown blocked-word dataset.")
    all_terms: list[str] = []
    for url in dataset["urls"]:
        request = Request(
            url,
            headers={"User-Agent": "MemactAutoMod/1.0"},
        )
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, list):
            raise ValueError("The blocked-word dataset returned an unexpected format.")
        all_terms.extend(str(item) for item in payload)
    return normalize_blocked_terms(all_terms)
