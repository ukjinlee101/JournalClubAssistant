"""Summary extraction from paper abstracts."""

import re


def strip_html(text: str) -> str:
    """Remove HTML/XML tags from text (CrossRef abstracts often contain JATS XML)."""
    if not text:
        return ""
    # Remove XML/HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def extract_summary(abstract: str) -> str:
    """Extract the first sentence from an abstract as a one-sentence summary.

    Args:
        abstract: Raw abstract text (may contain HTML tags).

    Returns:
        First sentence of the abstract, or a fallback message.
    """
    if not abstract or not abstract.strip():
        return "No abstract available."

    clean = strip_html(abstract)

    if not clean:
        return "No abstract available."

    # Split on sentence-ending punctuation followed by a space or end-of-string.
    # We look for: period, exclamation, or question mark followed by a space
    # and an uppercase letter (to avoid splitting on abbreviations like "e.g.").
    # Fallback: if no match, just return the cleaned text truncated.
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', clean, maxsplit=1)

    first_sentence = sentences[0].strip()

    # Ensure it ends with punctuation
    if first_sentence and first_sentence[-1] not in ".!?":
        first_sentence += "."

    # Cap length at ~300 chars for readability
    if len(first_sentence) > 300:
        first_sentence = first_sentence[:297] + "..."

    return first_sentence
