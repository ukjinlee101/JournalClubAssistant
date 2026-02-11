# Journal Club Assistant

Scan your favorite academic journals for recently published papers, filter by your research keywords, and interactively curate a reading list — all from the command line.

## Setup

### 1. Install Docker

Download and install Docker Desktop: [https://docs.docker.com/desktop/setup/install/mac-install/](https://docs.docker.com/desktop/setup/install/mac-install/)

### 2. Edit `config.yaml`

Add your journals (name + ISSN), keywords, and search duration:

```yaml
journals:
  - name: "Nature"
    issn: "0028-0836"

keywords:
  - "chromatin"
  - "stem cell"

search_days: 30
```

You can find ISSNs on the journal's website or at [portal.issn.org](https://portal.issn.org).

### 3. Run

```bash
./run.sh
```

This will build a Docker image (first run only), fetch papers, and walk you through each one interactively — press **y** to keep, **n** to skip, **q** to quit early. Accepted papers are saved to a date-stamped CSV file.

**Additional options:**
```bash
./run.sh --no-review              # Skip review, save all matches
./run.sh --days 7                 # Search last 7 days only
./run.sh --output my_picks.csv    # Custom output filename
```

## How It Works

1. Fetches recent papers from each journal via the [CrossRef API](https://www.crossref.org/documentation/)
2. Filters papers whose title or abstract match any of your keywords
3. Presents each paper interactively — you decide **keep** or **skip**
4. Saves only your accepted papers to a date-stamped CSV file
