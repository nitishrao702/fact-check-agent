# The Fact-Check Agent — Truth Layer Application

An automated tool built to parse document uploads, extract strategic/marketing metrics, verify assertions against live search engine results, and flag data discrepancies[cite: 3].

## Core Capabilities
- **Extraction:** Automatically extracts complex claims using `pypdf` and text analytics frameworks[cite: 3].
- **Live Search Verification:** Connects to live indices via `duckduckgo_search` to verify claims without static delays[cite: 3].
- **Classification Engine:** Categorizes targets into `VERIFIED`, `INACCURATE`, or `FALSE` statuses[cite: 3].

## Local Installation
1. Clone this repository to your local system.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
