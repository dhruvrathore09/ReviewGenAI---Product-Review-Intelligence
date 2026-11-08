"""Rule-based directional valence-shifting aspect sentiment scorer.

Enforces:
- Complete exclusion of Level 5 ML model.
- Directional Negation-Collocation Matrix (beyond naive inversion).
- Cognitive verb negative raising ('I don't think ... is good').
- Correlative conjunction addition ('not only good but excellent').
- Heuristic composite confidence index ($C \in [0.00, 1.00]$).
- Mutually exclusive thresholds: High (>=0.70), Moderate (>=0.60), Uncertain (<0.60).
- Purely factual/descriptive mentions classified as Neutral.
"""

import re
from typing import Any, Dict, List, Tuple

from src.absa.config import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MINIMUM,
    CONFIDENCE_MODERATE,
    SENTIMENT_NEGATIVE,
    SENTIMENT_NEUTRAL,
    SENTIMENT_POSITIVE,
    SENTIMENT_UNCERTAIN,
)
from src.absa.context_analysis import (
    detect_modifiers,
    find_negation_in_tokens,
    has_cognitive_negation,
    is_correlative_not_only,
)

# 1. Lexical Polarity Dictionaries
POSITIVE_LEXICON = {
    "excellent",
    "great",
    "good",
    "amazing",
    "fantastic",
    "superb",
    "wonderful",
    "awesome",
    "flawless",
    "stellar",
    "solid",
    "clear",
    "crisp",
    "sharp",
    "bright",
    "vivid",
    "fast",
    "quick",
    "sturdy",
    "durable",
    "tough",
    "robust",
    "affordable",
    "worth",
    "bargain",
    "steal",
    "pleased",
    "happy",
    "satisfied",
    "love",
    "liked",
    "enjoy",
    "recommend",
    "impressive",
    "convenient",
    "nice",
    "decent",
    "fine",
    "perfect",
    "reasonable",
}

NEGATIVE_LEXICON = {
    "terrible",
    "horrible",
    "awful",
    "bad",
    "poor",
    "disappointing",
    "disappointed",
    "worse",
    "worst",
    "useless",
    "worthless",
    "broke",
    "broken",
    "flimsy",
    "fragile",
    "cheaply",
    "dim",
    "dull",
    "blurry",
    "muffled",
    "static",
    "distortion",
    "slow",
    "sluggish",
    "laggy",
    "drain",
    "drained",
    "dead",
    "waste",
    "overpriced",
    "expensive",
    "pricey",
    "defective",
    "faulty",
    "died",
    "fails",
    "failed",
    "unusable",
    "scratch",
    "scratched",
    "crack",
    "cracked",
    "snapped",
    "buzzing",
}

# Function failure verbs (when negated -> strong negative)
FAILURE_VERBS = {
    "work",
    "working",
    "charge",
    "charging",
    "hold",
    "holding",
    "connect",
    "connecting",
    "pair",
    "pairing",
    "turn",
    "power",
    "function",
    "hear",
}

# Explicit double-negative / attenuated positive collocations
DOUBLE_NEGATIVE_POSITIVES = {
    "not bad",
    "not a bad",
    "not expensive",
    "not too expensive",
    "not heavy",
    "not too heavy",
    "not flimsy",
    "not cheap feeling",
}


def score_clause_sentiment(clause_text: str, aspect: str, matched_term: str) -> Dict[str, Any]:
    """Score the aspect-level sentiment for a specific clause.
    
    Args:
        clause_text: The grammatical sub-clause containing the aspect mention.
        aspect: The aspect category (e.g. 'battery', 'sound_quality').
        matched_term: The exact term that triggered the aspect anchor.
        
    Returns:
        Dictionary with 'sentiment', 'confidence', 'polarity_score', and 'reason'.
    """
    clean_clause = clause_text.lower().strip()
    words = re.findall(r"\b[a-z']+\b", clean_clause)

    if not words:
        return {
            "sentiment": SENTIMENT_NEUTRAL,
            "confidence": CONFIDENCE_HIGH,
            "polarity_score": 0.0,
            "reason": "empty_clause",
        }

    # Step 1: Check for explicit double-negative positives
    for dnp in DOUBLE_NEGATIVE_POSITIVES:
        if dnp in clean_clause:
            return {
                "sentiment": SENTIMENT_POSITIVE,
                "confidence": CONFIDENCE_HIGH,
                "polarity_score": 0.75,
                "reason": f"double_negative_positive: '{dnp}'",
            }

    # Step 2: Check for correlative addition ('not only X but excellent')
    if is_correlative_not_only(clean_clause):
        return {
            "sentiment": SENTIMENT_POSITIVE,
            "confidence": 0.85,
            "polarity_score": 0.85,
            "reason": "correlative_not_only_addition",
        }

    # Step 3: Check for cognitive matrix verb negative raising ('I don't think ... is good')
    cog_neg = has_cognitive_negation(clean_clause)

    # Step 4: Lexical Scan with Directional Negation
    pos_matches: List[Tuple[str, int]] = []
    neg_matches: List[Tuple[str, int]] = []
    has_intensifier = False
    has_diminisher = False

    for idx, w in enumerate(words):
        is_neg, negator = find_negation_in_tokens(words, idx, window_size=3)

        # Apply cognitive verb negative raising
        if cog_neg and w in POSITIVE_LEXICON:
            is_neg = True

        mods = detect_modifiers(words, idx, window_size=2)
        if mods["has_intensifier"]:
            has_intensifier = True
        if mods["has_diminisher"]:
            has_diminisher = True

        if w in POSITIVE_LEXICON:
            if is_neg:
                # Negated positive -> negative ('not good', 'not clear')
                neg_matches.append((f"{negator}_{w}", idx))
            else:
                pos_matches.append((w, idx))

        elif w in NEGATIVE_LEXICON:
            if is_neg:
                # Negated negative -> mild positive ('not terrible', 'not bad')
                pos_matches.append((f"{negator}_{w}", idx))
            else:
                neg_matches.append((w, idx))

        elif w in FAILURE_VERBS and is_neg:
            # Negated function verb -> strong negative ('does not charge', 'won't work')
            neg_matches.append((f"{negator}_{w}", idx))

    # Step 5: Determine Sentiment and Compute Heuristic Confidence Index
    num_pos = len(pos_matches)
    num_neg = len(neg_matches)

    # Anchor strength bonus
    anchor_bonus = 0.50 if " " in matched_term else 0.35

    # Case A: Purely Descriptive / Factual Mention (Zero Sentiment Cues)
    if num_pos == 0 and num_neg == 0:
        return {
            "sentiment": SENTIMENT_NEUTRAL,
            "confidence": 0.80,
            "polarity_score": 0.0,
            "reason": "factual_descriptive_no_sentiment_cues",
        }

    # Case B: Conflicting Signals in the Same Clause (Mixed / Ambiguous)
    if num_pos > 0 and num_neg > 0:
        confidence = max(0.40, anchor_bonus + 0.30 - 0.40)
        sentiment = SENTIMENT_UNCERTAIN if confidence < CONFIDENCE_MINIMUM else SENTIMENT_NEUTRAL
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "polarity_score": 0.0,
            "reason": f"conflicting_cues (pos={num_pos}, neg={num_neg})",
        }

    # Case C: Positive Sentiment
    if num_pos > 0 and num_neg == 0:
        base_c = anchor_bonus + 0.40
        if has_intensifier:
            base_c += 0.10
        if has_diminisher:
            base_c -= 0.10
        confidence = min(0.95, max(0.50, base_c))
        sentiment = SENTIMENT_POSITIVE if confidence >= CONFIDENCE_MINIMUM else SENTIMENT_UNCERTAIN
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "polarity_score": round(confidence, 2),
            "reason": f"positive_cue: {[m[0] for m in pos_matches]}",
        }

    # Case D: Negative Sentiment
    if num_neg > 0 and num_pos == 0:
        base_c = anchor_bonus + 0.40
        if has_intensifier:
            base_c += 0.10
        if has_diminisher:
            base_c -= 0.10
        confidence = min(0.95, max(0.50, base_c))
        sentiment = SENTIMENT_NEGATIVE if confidence >= CONFIDENCE_MINIMUM else SENTIMENT_UNCERTAIN
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "polarity_score": round(-confidence, 2),
            "reason": f"negative_cue: {[m[0] for m in neg_matches]}",
        }

    return {
        "sentiment": SENTIMENT_UNCERTAIN,
        "confidence": 0.40,
        "polarity_score": 0.0,
        "reason": "unhandled_fallback",
    }
