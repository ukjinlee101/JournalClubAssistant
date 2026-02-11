"""Journal Club Assistant — CLI entry point."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import Config
from .crossref_client import CrossRefClient
from .filter import FilteredPaper, filter_papers
from .formatter import export_csv, export_markdown
from .summarizer import extract_summary, strip_html


def _generate_output_path(ext: str = ".csv") -> Path:
    """Generate an output filename based on current date and time."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return Path(f"results_{timestamp}{ext}")


def _display_paper(fp: FilteredPaper, index: int, total: int, console: Console) -> None:
    """Display a single paper for interactive review."""
    paper = fp.paper
    abstract_clean = strip_html(paper.abstract) if paper.abstract else "No abstract available."
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
    table.add_row("Abstract", abstract_clean)
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
            title=f"[bold]Paper {index}/{total}[/bold]",
            border_style="blue",
            expand=True,
        )
    )


def _interactive_review(
    filtered: list[FilteredPaper],
    console: Console,
) -> list[FilteredPaper]:
    """Interactively review papers one-by-one. Returns only accepted papers."""
    if not filtered:
        return []

    console.print()
    console.print(
        Panel(
            "[bold]Interactive Review Mode[/bold]\n"
            "For each paper: [green]y[/green] = keep, "
            "[red]n[/red] = skip, "
            "[yellow]q[/yellow] = quit (save what's accepted so far)",
            border_style="bright_blue",
        )
    )
    console.print()

    accepted: list[FilteredPaper] = []
    total = len(filtered)

    for i, fp in enumerate(filtered, 1):
        _display_paper(fp, i, total, console)

        while True:
            choice = Prompt.ask(
                f"  [bold]Keep this paper?[/bold] [green]y[/green]/[red]n[/red]/[yellow]q[/yellow]",
                choices=["y", "n", "q"],
                default="y",
                console=console,
            )
            break

        if choice == "q":
            console.print(f"\n[yellow]Stopped at paper {i}/{total}.[/yellow]")
            break
        elif choice == "y":
            accepted.append(fp)
            console.print(f"  [green]✓ Accepted[/green]  ({len(accepted)} kept so far)\n")
        else:
            console.print(f"  [dim]✗ Skipped[/dim]\n")

    console.print(
        Panel(
            f"[bold green]Review complete: {len(accepted)}/{total} paper(s) accepted[/bold green]",
            border_style="green",
        )
    )
    return accepted


def _save_results(
    papers: list[FilteredPaper],
    output_arg: str | None,
    console: Console,
) -> None:
    """Save results to file, auto-generating a dated filename if needed."""
    if output_arg:
        output_path = Path(output_arg)
    else:
        output_path = _generate_output_path(".csv")

    if output_path.suffix.lower() == ".md":
        out_path = export_markdown(papers, output_path)
    else:
        if output_path.suffix.lower() != ".csv":
            output_path = output_path.with_suffix(".csv")
        out_path = export_csv(papers, output_path)

    console.print(
        f"\n[bold green]✓[/bold green] Results saved to "
        f"[link=file://{out_path}]{out_path}[/link]"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="journal-club",
        description=(
            "Scan academic journals for recently published papers, "
            "filter by your keywords, and get a curated reading list."
        ),
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the YAML configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Override search_days from config (how many days back to search)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save results (use .csv or .md; auto-generated with date if omitted)",
    )
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Skip interactive review and save all matched papers directly",
    )
    args = parser.parse_args()

    console = Console()

    # ── Load config ─────────────────────────────────────────────────────
    try:
        config = Config.from_yaml(args.config)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Configuration error:[/bold red] {e}")
        sys.exit(1)

    if args.days is not None:
        config.search_days = args.days

    # ── Print banner ────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel(
            "[bold]Journal Club Assistant[/bold]\n"
            f"Scanning [cyan]{len(config.journals)}[/cyan] journal(s) "
            f"for papers from the last [cyan]{config.search_days}[/cyan] days\n"
            f"Filtering by [cyan]{len(config.keywords)}[/cyan] keyword(s)",
            border_style="bright_blue",
        )
    )
    console.print()

    # ── Fetch papers ────────────────────────────────────────────────────
    client = CrossRefClient(email=config.email)
    all_papers = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for journal in config.journals:
            task_id = progress.add_task(
                f"Fetching from [bold]{journal.name}[/bold] ({journal.issn})…"
            )
            papers = client.fetch_recent_papers(
                issn=journal.issn,
                journal_name=journal.name,
                days_back=config.search_days,
            )
            progress.update(task_id, completed=True, visible=False)
            console.print(
                f"  ✓  [bold]{journal.name}[/bold]: "
                f"fetched [green]{len(papers)}[/green] recent paper(s)"
            )
            all_papers.extend(papers)

    console.print()
    console.print(
        f"Total papers fetched: [bold]{len(all_papers)}[/bold] across "
        f"{len(config.journals)} journal(s)"
    )

    # ── Filter by keywords ──────────────────────────────────────────────
    filtered = filter_papers(all_papers, config.keywords)
    console.print(
        f"Papers matching your keywords: [bold green]{len(filtered)}[/bold green]"
    )

    if not filtered:
        console.print(
            Panel(
                "[yellow]No papers matched your keywords.[/yellow]\n"
                "Try broadening your keywords or increasing the search duration.",
                title="No Results",
                border_style="yellow",
            )
        )
        return

    # ── Interactive review or direct save ───────────────────────────────
    if args.no_review:
        final_papers = filtered
    else:
        final_papers = _interactive_review(filtered, console)

    if not final_papers:
        console.print("[yellow]No papers to save.[/yellow]")
        return

    # ── Save results ────────────────────────────────────────────────────
    _save_results(final_papers, args.output, console)


if __name__ == "__main__":
    main()
