# Journal Club Assistant

Scan your favorite academic journals for recently published papers, filter by your research keywords, and interactively curate a reading list — all from the command line.

## Quick Start

```bash
# Just run it — the script auto-sets up a virtual environment on first run:
./run.sh

# Skip interactive review (save all matched papers):
./run.sh --no-review

# Override search duration:
./run.sh --days 7

# Custom output file:
./run.sh --output my_picks.csv
```

Output files are auto-named with date and time (e.g., `results_2026-02-10_213906.csv`).

## Deploy to Another Machine

### Option A: Docker (recommended — no Python setup needed)

```bash
# If Docker is installed, ./run.sh uses it automatically.
# Or build and run manually:
docker build -t journal-club .
docker run --rm -it -v ./config.yaml:/app/config.yaml:ro -v .:/app/output journal-club
```

### Option B: Virtual environment (no Docker)

```bash
# ./run.sh auto-creates a venv on first run. Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Configuration

Edit `config.yaml` to customize:

- **journals** — list of journals (name + ISSN)
- **keywords** — terms to match against titles and abstracts
- **search_days** — how far back to search (default: 30)
- **email** — optional, for faster CrossRef API access

## How It Works

1. Fetches recent papers from each journal via the [CrossRef API](https://www.crossref.org/documentation/)
2. Filters papers whose title or abstract match any of your keywords
3. Presents each paper interactively — you decide **keep** or **skip**
4. Saves only your accepted papers to a date-stamped CSV file
