# Journal Club Assistant

Scan your favorite academic journals for recently published papers, filter by your research keywords, and interactively curate a reading list — all from the command line.

## Setup

### 1. Install Docker

Docker is a tool that packages this application with everything it needs to run, so you don't have to worry about installing Python or any dependencies. It works the same on every Mac.

Download and install Docker Desktop: [https://docs.docker.com/desktop/setup/install/mac-install/](https://docs.docker.com/desktop/setup/install/mac-install/)

After installing, **open Docker Desktop** and wait for it to start (you'll see the whale icon in your menu bar).

### 2. Download this repository

Open **Terminal** (search for "Terminal" in Spotlight) and run:

```bash
git clone https://github.com/ukjinlee101/JournalClubAssistant.git
cd JournalClubAssistant
```

This downloads the project to your computer. You only need to do this once.

### 3. Edit `config.yaml`

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

### 4. Run

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

## Updating

When a new version is available, open Terminal, go to the project folder, and run:

```bash
cd JournalClubAssistant
git pull
docker rmi journal-club-assistant
./run.sh
```

- `git pull` downloads the latest code from GitHub
- `docker rmi journal-club-assistant` removes the old Docker image so it gets rebuilt with the updates
- `./run.sh` rebuilds and runs as usual
