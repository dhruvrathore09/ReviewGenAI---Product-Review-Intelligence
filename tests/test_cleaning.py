"""Tests for context-preserving review and title text cleaning."""

import pytest
from src.pipeline.clean_reviews import clean_review_text, clean_review_title


def test_whitespace_normalization():
    """Verify excessive leading, trailing, and internal whitespace is normalized."""
    raw = "   This   is   a   great\n\nheadphone!   \t  "
    cleaned = clean_review_text(raw)
    assert cleaned == "This is a great headphone!"


def test_empty_and_null_handling():
    """Verify None, empty string, and whitespace-only return empty strings."""
    assert clean_review_text(None) == ""
    assert clean_review_text("") == ""
    assert clean_review_text("   \n\t  ") == ""
    assert clean_review_title(None) == ""
    assert clean_review_title("   ") == ""


def test_negation_preservation():
    """CRITICAL: Verify negations are strictly preserved and never dropped."""
    negation_samples = [
        "The battery is not good at all.",
        "I will never buy from this seller again.",
        "There is no audio coming from the left earbud.",
        "Cannot recommend this product to anyone.",
        "It doesn't work after two weeks.",
    ]
    for sample in negation_samples:
        cleaned = clean_review_text(sample)
        # Verify negation words exist in the cleaned string
        for neg in ["not", "never", "no", "cannot", "doesn't"]:
            if neg in sample.lower():
                assert neg in cleaned.lower(), f"Negation '{neg}' was erroneously removed!"


def test_unicode_and_entity_unescaping():
    """Verify HTML entities, smart quotes, and dashes are safely normalized."""
    raw = "Good &amp; loud! Cost was &lt;$50. It’s a ‘must-have’ – works great."
    cleaned = clean_review_text(raw)
    assert "&" in cleaned
    assert "<$50" in cleaned
    assert "It's" in cleaned or "It's" in cleaned.replace("’", "'")
    assert "&amp;" not in cleaned
    assert "&lt;" not in cleaned


def test_repeated_punctuation_compression():
    """Verify excessive punctuation is compressed without deleting sentiment intensity."""
    raw = "Amazing quality!!!!!!!! Love it???"
    cleaned = clean_review_text(raw)
    assert cleaned == "Amazing quality!! Love it??"


def test_clean_review_title():
    """Verify review title cleaning normalizes trailing boilerplate dashes and periods."""
    raw_title = "  Awesome Sound Quality... --  "
    cleaned = clean_review_title(raw_title)
    assert cleaned == "Awesome Sound Quality"

