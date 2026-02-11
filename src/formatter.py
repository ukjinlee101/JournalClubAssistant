"""Output formatting — Rich console tables, CSV export, and Markdown export."""

import csv
from datetime import datetime
from io import StringIO
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .crossref_client import Paper
from .filter import FilteredPaper
from .summarizer import extract_summary


def print_results(filtered_papers: list[FilteredPaper], console: Console | None = None) -> None:
    """Print filtered papers as a beautiful Rich table to the console.

    Args:
        filtered_papers: List of FilteredPaper results to display.
        console: Optional Rich Console instance (creates one if not provided).
    """
    if console is None:
        console = Console()

    if not filtered_papers:
        console.print(
            Panel(
                "[yellow]No papers matched your keywords.[/yellow]\n"
                "Try broadening your keywords or increasing the search duration.",
                title="No Results",
                border_style="yellow",
            )
        )
        return

    console.print()
    console.print(
        Panel(
            f"[bold green]Found {len(filtered_papers)} paper(s) matching your interests[/bold green]",
            border_style="green",
        )
    )
    console.print()

    for i, fp in enumerate(filtered_papers, 1):
        paper = fp.paper
        summary = extract_summary(paper.abstract)
        keywords_str = ", ".join(fp.matched_keywords) if fp.matched_keywords else "—"

        table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
            expand=True,
        )
        table.add_column("Field", style="bold cyan", width=12, no_wrap=True)
        table.add_column("Value")

        table.add_row("Title", paper.title)
        table.add_row("Journal", paper.journal_name)
        table.add_row("Published", paper.published_date or "—")
        table.add_row("Summary", summary)
        table.add_row("Keywords", f"[magenta]{keywords_str}[/magenta]")
        table.add_row("Link", f"[link={paper.url}]{paper.url}[/link]")

        if paper.authors:
            authors_display = ", ".join(paper.authors[:5])
            if len(paper.authors) > 5:
                authors_display += f" (+{len(paper.authors) - 5} more)"
            table.add_row("Authors", authors_display)

        console.print(
            Panel(
                table,
                title=f"[bold]#{i}[/bold]",
                border_style="blue",
                expand=True,
            )
        )
        console.print()


def export_markdown(
    filtered_papers: list[FilteredPaper],
    output_path: str | Path,
) -> Path:
    """Export filtered papers to a Markdown file.

    Args:
        filtered_papers: List of FilteredPaper results to export.
        output_path: Path where the Markdown file will be written.

    Returns:
        Path to the created file.
    """
    output_path = Path(output_path)
    today = datetime.now().strftime("%Y-%m-%d")

    lines: list[str] = []
    lines.append(f"# Journal Club — Papers of Interest")
    lines.append(f"")
    lines.append(f"*Generated on {today} — {len(filtered_papers)} paper(s) found*")
    lines.append("")

    if not filtered_papers:
        lines.append("No papers matched your keywords.")
    else:
        lines.append("| # | Title | Journal | Summary | Keywords | Link |")
        lines.append("|---|-------|---------|---------|----------|------|")

        for i, fp in enumerate(filtered_papers, 1):
            paper = fp.paper
            summary = extract_summary(paper.abstract)
            keywords_str = ", ".join(fp.matched_keywords) if fp.matched_keywords else "—"

            # Escape pipes in content for markdown table
            title_safe = paper.title.replace("|", "\\|")
            summary_safe = summary.replace("|", "\\|")
            journal_safe = paper.journal_name.replace("|", "\\|")

            link = f"[Link]({paper.url})" if paper.url else "—"
            lines.append(
                f"| {i} | {title_safe} | {journal_safe} | {summary_safe} | {keywords_str} | {link} |"
            )

    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def export_csv(
    filtered_papers: list[FilteredPaper],
    output_path: str | Path,
) -> Path:
    """Export filtered papers to a CSV file.

    Args:
        filtered_papers: List of FilteredPaper results to export.
        output_path: Path where the CSV file will be written.

    Returns:
        Path to the created file.
    """
    output_path = Path(output_path)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Journal", "Published", "Summary", "Keywords", "Link", "Authors"])

        for fp in filtered_papers:
            paper = fp.paper
            summary = extract_summary(paper.abstract)
            keywords_str = ", ".join(fp.matched_keywords) if fp.matched_keywords else ""
            authors_str = ", ".join(paper.authors) if paper.authors else ""

            writer.writerow([
                paper.title,
                paper.journal_name,
                paper.published_date or "",
                summary,
                keywords_str,
                paper.url,
                authors_str,
            ])

    return output_path

