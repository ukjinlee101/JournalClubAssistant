"""CrossRef API client for fetching recent journal papers."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import re

import requests


CROSSREF_API_BASE = "https://api.crossref.org"


@dataclass
class Paper:
    """Represents a single academic paper."""
    title: str
    doi: str
    url: str
    abstract: str
    published_date: str
    journal_name: str
    authors: list[str] = field(default_factory=list)


class CrossRefClient:
    """Client for the CrossRef REST API."""

    def __init__(self, email: str = ""):
        self.session = requests.Session()
        # Set polite headers
        user_agent = "JournalClubAssistant/1.0"
        if email:
            user_agent += f" (mailto:{email})"
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })

    def fetch_recent_papers(
        self,
        issn: str,
        journal_name: str,
        days_back: int = 30,
        max_results: int = 100,
    ) -> list[Paper]:
        """Fetch papers published in the last `days_back` days from a journal.

        Args:
            issn: The journal's ISSN.
            journal_name: Human-readable journal name (used as fallback).
            days_back: How many days back to search.
            max_results: Maximum number of papers to return.

        Returns:
            List of Paper objects.
        """
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = f"{CROSSREF_API_BASE}/journals/{issn}/works"
        params = {
            "filter": f"from-pub-date:{from_date}",
            "rows": min(max_results, 100),  # CrossRef max per page is 100
            "sort": "published",
            "order": "desc",
            "cursor": "*",
        }

        papers: list[Paper] = []

        while len(papers) < max_results:
            try:
                resp = self.session.get(url, params=params, timeout=30)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"  ⚠  Error fetching from CrossRef for ISSN {issn}: {e}")
                break

            data = resp.json()
            message = data.get("message", {})
            items = message.get("items", [])

            if not items:
                break

            for item in items:
                paper = self._parse_item(item, journal_name)
                if paper:
                    papers.append(paper)

            # Cursor-based pagination
            next_cursor = message.get("next-cursor")
            if not next_cursor or len(items) < params["rows"]:
                break
            params["cursor"] = next_cursor

        return papers[:max_results]

    def _parse_item(self, item: dict, fallback_journal: str) -> Optional[Paper]:
        """Parse a CrossRef work item into a Paper object."""
        # Title (may contain HTML tags like <i> for species names)
        titles = item.get("title", [])
        title = titles[0] if titles else ""
        if not title:
            return None
        # Strip HTML/XML tags from title and collapse whitespace
        title = re.sub(r"<[^>]+>", "", title)
        title = re.sub(r"\s+", " ", title).strip()

        # DOI and URL
        doi = item.get("DOI", "")
        url = f"https://doi.org/{doi}" if doi else item.get("URL", "")

        # Abstract (may contain HTML/JATS XML tags)
        abstract = item.get("abstract", "")

        # Published date
        published_date = ""
        date_parts = None
        for date_field in ("published-print", "published-online", "published"):
            if date_field in item:
                date_parts = item[date_field].get("date-parts", [[]])
                break
        if date_parts and date_parts[0]:
            parts = date_parts[0]
            if len(parts) >= 3:
                published_date = f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}"
            elif len(parts) >= 2:
                published_date = f"{parts[0]}-{parts[1]:02d}"
            elif len(parts) >= 1:
                published_date = str(parts[0])

        # Journal name
        journal_name = ""
        container = item.get("container-title", [])
        if container:
            journal_name = container[0]
        if not journal_name:
            journal_name = fallback_journal

        # Authors
        authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if given and family:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)

        return Paper(
            title=title,
            doi=doi,
            url=url,
            abstract=abstract,
            published_date=published_date,
            journal_name=journal_name,
            authors=authors,
        )
