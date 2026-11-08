"""Curated, contextually gated aspect lexicon and multi-word pattern matcher.

Enforces strict disambiguation rules:
- Standalone 'monitor' is removed (requires display-specific collocations).
- Standalone 'power' is removed (requires battery-specific collocations).
- Idiomatic 'sounds like', 'sound advice', 'free of charge', 'in charge' are blacklisted.
- Mechanical sounds ('keys make a sound') and inventory ('comes with charger') are blacklisted.
- Passive component presence ('speakers in place') without evaluative feedback is filtered out.
"""

import re
from typing import Dict, List, Pattern

from src.absa.config import (
    ASPECT_BATTERY,
    ASPECT_BUILD,
    ASPECT_CATEGORIES,
    ASPECT_DISPLAY,
    ASPECT_PRICE,
    ASPECT_SOUND,
)

# 1. Curated Domain Lexicon mapping aspect categories to unambiguous terms & phrases.
# Sorted by multi-word expression length first to guarantee compound matching precedence.
ASPECT_LEXICON: Dict[str, List[str]] = {
    ASPECT_BATTERY: [
        # Explicit multi-word battery & charging performance expressions
        "battery life",
        "battery backup",
        "battery drain",
        "battery dying",
        "battery dead",
        "dead battery",
        "holds a charge",
        "holds charge",
        "holding a charge",
        "holding charge",
        "fast charging",
        "quick charging",
        "fast charge",
        "quick charge",
        "slow charging",
        "charges slowly",
        "charges fast",
        "charges quickly",
        "charging speed",
        "charging time",
        "battery capacity",
        "power consumption",
        "rechargeable battery",
        "takes a charge",
        "wont charge",
        "won't charge",
        "stopped charging",
        "drain fast",
        "drains quickly",
        # Unambiguous component keywords
        "battery",
        "batteries",
        "rechargeable",
        "recharge",
        "recharging",
        "mah",
        "runtime",
    ],
    ASPECT_SOUND: [
        # Multi-word sound & audio expressions
        "sound quality",
        "audio quality",
        "noise cancelling",
        "noise cancellation",
        "sound level",
        "sound clarity",
        "voice clarity",
        "bass response",
        "bass level",
        "microphone quality",
        "mic quality",
        "audio output",
        "sound stage",
        "soundstage",
        "volume level",
        # Component & acoustic keywords (excluding linking verb 'sounds')
        "audio",
        "speaker",
        "speakers",
        "volume",
        "bass",
        "treble",
        "microphone",
        "mics",
        "clarity",
        "acoustic",
        "acoustics",
        "muffled",
        "stereo",
        "subwoofer",
        "headphone",
        "headphones",
        "earphone",
        "earphones",
        "earbud",
        "earbuds",
        "static",
        "distortion",
        "buzzing",
    ],
    ASPECT_BUILD: [
        # Multi-word build & durability expressions
        "build quality",
        "well made",
        "poorly made",
        "solid construction",
        "poor construction",
        "solid build",
        "cheap build",
        "cheap feel",
        "premium feel",
        "fell apart",
        "broke after",
        "stopped working",
        "holding up well",
        # Component & physical durability keywords
        "durability",
        "durable",
        "sturdy",
        "fragile",
        "flimsy",
        "solid",
        "aluminum",
        "casing",
        "hinge",
        "hinges",
        "scratch",
        "scratches",
        "scratched",
        "cracked",
        "crack",
        "snapped",
        "robust",
        "tough",
    ],
    ASPECT_DISPLAY: [
        # Multi-word screen & visual quality expressions (eliminates ambiguous standalone 'monitor')
        "picture quality",
        "image quality",
        "screen resolution",
        "display quality",
        "viewing angle",
        "refresh rate",
        "anti glare",
        "color accuracy",
        "touch response",
        "touch screen",
        "touchscreen",
        "oled display",
        "oled screen",
        "lcd screen",
        "lcd display",
        "monitor display",
        "monitor screen",
        "screen brightness",
        "display brightness",
        # Unambiguous screen visual keywords
        "display",
        "screen",
        "screens",
        "brightness",
        "resolution",
        "oled",
        "lcd",
        "pixel",
        "pixels",
        "backlight",
    ],
    ASPECT_PRICE: [
        # Multi-word price & value evaluation expressions
        "waste of money",
        "worth the money",
        "worth every penny",
        "worth every cent",
        "worth the price",
        "bang for the buck",
        "bang for your buck",
        "value for money",
        "good buy",
        "great buy",
        "bad buy",
        "rip off",
        "reasonably priced",
        "over priced",
        "fair price",
        "good value",
        "great value",
        "poor value",
        "best price",
        # Value & financial evaluative adjectives
        "expensive",
        "inexpensive",
        "affordable",
        "overpriced",
        "pricey",
        "economical",
        "budget",
        "bargain",
        "steal",
        "price",
        "prices",
    ],
}

# 2. Blacklisted Idioms, Incidental Mechanical Sounds, Peripheral Contexts & Passive Layouts
BLACK_LISTED_PATTERNS: Dict[str, List[Pattern]] = {
    ASPECT_BATTERY: [
        re.compile(r"\b(comes?\s+with(\s+a)?\s+charger)\b", re.IGNORECASE),
        re.compile(r"\b(charger\s+(is\s+)?included)\b", re.IGNORECASE),
        re.compile(r"\b(in\s+charge\s+of)\b", re.IGNORECASE),
        re.compile(r"\b(free\s+of\s+charge)\b", re.IGNORECASE),
        re.compile(r"\b(no(\s+extra)?\s+charge)\b", re.IGNORECASE),
        re.compile(r"\b(extra\s+charge)\b", re.IGNORECASE),
        re.compile(r"\b(power\s+(cord|supply|button|outlet|strip))\b", re.IGNORECASE),
        # Cable accessory specification without battery performance evaluation
        re.compile(r"\b(charging\s+(cord|cable|wire|block))\b(?!.*?\b(battery|phone|charge\s+fast|drains)\b)", re.IGNORECASE),
    ],
    ASPECT_SOUND: [
        re.compile(r"\b(sounds?\s+(like|as\s+if|promising|interesting|familiar))\b", re.IGNORECASE),
        re.compile(r"\b(sound\s+advice)\b", re.IGNORECASE),
        re.compile(r"\b(safe\s+and\s+sound)\b", re.IGNORECASE),
        re.compile(r"\b(sound\s+asleep)\b", re.IGNORECASE),
        # Incidental mechanical noise (e.g. keyboard typing clicks)
        re.compile(r"\b(keys?|buttons?|fan|hinge|wheel)\s+(make|makes|made)\s+(a\s+)?sound\b", re.IGNORECASE),
        re.compile(r"\b(clicking|rattling|grinding|beeping)\s+(sound|noise)\b", re.IGNORECASE),
        # Passive component presence without evaluative feedback
        re.compile(r"\b(all\s+speakers\s+in\s+place)\b", re.IGNORECASE),
        re.compile(r"\b(speakers?\s+in\s+place)\b", re.IGNORECASE),
        re.compile(r"\b(speaker\s+location)\b", re.IGNORECASE),
    ],
    ASPECT_BUILD: [
        re.compile(r"\b(reading\s+material)\b", re.IGNORECASE),
        re.compile(r"\b(marketing\s+material)\b", re.IGNORECASE),
        re.compile(r"\b(raw\s+material)\b", re.IGNORECASE),
    ],
    ASPECT_DISPLAY: [
        # Disambiguates cables/cords connecting to an external monitor without display feedback
        re.compile(r"\b(cable|cord|adapter|plug|mount)\s+(for|to)\s+(my\s+)?(external\s+)?(monitor|tv|screen)\b", re.IGNORECASE),
        re.compile(r"\b(works?\s+(great|well)\s+for\s+(my\s+)?(external\s+)?(monitor|tv))\b", re.IGNORECASE),
    ],
    ASPECT_PRICE: [
        re.compile(r"\b(in\s+charge)\b", re.IGNORECASE),
        re.compile(r"\b(at\s+no\s+cost)\b", re.IGNORECASE),
    ],
}


def is_blacklisted(clause: str, aspect: str) -> bool:
    """Check if the clause matches a known false-positive idiom, mechanical noise, or inventory blacklist."""
    patterns = BLACK_LISTED_PATTERNS.get(aspect, [])
    for pat in patterns:
        if pat.search(clause):
            return True
    return False


def compile_aspect_patterns() -> Dict[str, Pattern]:
    """Compile optimized regex patterns with word boundary enforcement.
    
    Terms are sorted by length descending so compound expressions
    (e.g., 'battery life', 'sound quality') are matched before single words.
    """
    patterns: Dict[str, Pattern] = {}
    for aspect in ASPECT_CATEGORIES:
        terms = ASPECT_LEXICON.get(aspect, [])
        sorted_terms = sorted(terms, key=len, reverse=True)
        escaped_terms = [re.escape(t) for t in sorted_terms]
        pattern_str = r"\b(" + "|".join(escaped_terms) + r")\b"
        patterns[aspect] = re.compile(pattern_str, re.IGNORECASE)
    return patterns


# Precompiled singleton dictionary for fast in-memory reuse
COMPILED_ASPECT_PATTERNS: Dict[str, Pattern] = compile_aspect_patterns()

