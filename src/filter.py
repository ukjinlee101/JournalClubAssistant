"""Keyword-based filtering engine for papers."""

from dataclasses import dataclass, field

from .crossref_client import Paper
from .summarizer import strip_html


@dataclass
class FilteredPaper:
    """A paper that passed keyword filtering, with matched keywords."""
    paper: Paper
    matched_keywords: list[str] = field(default_factory=list)


def filter_papers(papers: list[Paper], keywords: list[str]) -> list[FilteredPaper]:
    """Filter papers by checking if any keyword appears in the title or abstract.

    Matching is case-insensitive. Returns only papers where at least one
    keyword was found, along with which keywords matched.

    Args:
        papers: List of Paper objects to filter.
        keywords: List of keyword strings to search for.

    Returns:
        List of FilteredPaper objects that matched at least one keyword.
    """
    if not keywords:
        # No keywords configured — return all papers
        return [FilteredPaper(paper=p) for p in papers]

    results: list[FilteredPaper] = []
    lowercase_keywords = [kw.lower() for kw in keywords]

    for paper in papers:
        title_lower = paper.title.lower()
        abstract_lower = strip_html(paper.abstract).lower()

        matched = []
        for kw, kw_lower in zip(keywords, lowercase_keywords):
            if kw_lower in title_lower or kw_lower in abstract_lower:
                matched.append(kw)

        if matched:
            results.append(FilteredPaper(paper=paper, matched_keywords=matched))

    return results
