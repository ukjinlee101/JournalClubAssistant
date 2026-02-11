"""Configuration loader for Journal Club Assistant."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class JournalConfig:
    """A single journal to scan."""
    name: str
    issn: str


@dataclass
class Config:
    """Top-level configuration."""
    journals: list[JournalConfig]
    keywords: list[str]
    search_days: int = 30
    email: str = ""

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """Load configuration from a YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            raw = yaml.safe_load(f)

        if not raw:
            raise ValueError("Config file is empty")

        # Parse journals
        journals = []
        for j in raw.get("journals", []):
            if "name" not in j or "issn" not in j:
                raise ValueError(f"Each journal must have 'name' and 'issn': {j}")
            journals.append(JournalConfig(name=j["name"], issn=j["issn"]))

        if not journals:
            raise ValueError("At least one journal must be configured")

        keywords = raw.get("keywords", [])
        if not keywords:
            raise ValueError("At least one keyword must be configured")

        return cls(
            journals=journals,
            keywords=[kw.strip() for kw in keywords if kw.strip()],
            search_days=int(raw.get("search_days", 30)),
            email=raw.get("email", ""),
        )
