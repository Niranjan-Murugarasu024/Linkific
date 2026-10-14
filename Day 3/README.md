\# WebScrape — Python Web Scraping \& Data Cleaning



A beginner-friendly web scraping project built with Python, Requests, BeautifulSoup, and Pandas. The project extracts fictional bookstore listings, navigates paginated HTML pages, cleans the collected records, and exports structured datasets to CSV and JSON.



\## Features



\- HTML extraction with BeautifulSoup

\- CSS selectors for product data

\- Multi-page scraping with pagination

\- HTTP error handling and request timeouts

\- Duplicate removal and missing-value handling

\- Price conversion and price categorization

\- CSV and JSON data exports

\- Ethical scraping checklist



\## Technology Stack



\- Python

\- Requests

\- BeautifulSoup4

\- Pandas

\- CSV and JSON



\## Project Structure



```text

Day-3-WebScraping/

├── src/

│   ├── scraper.py

│   └── clean\_data.py

├── data/

│   ├── raw/

│   └── processed/

├── docs/

│   └── ethical\_scraping\_checklist.md

├── requirements.txt

├── .gitignore

└── README.md

```



\## Installation



Clone the repository and enter its directory:



```bash

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd Day-3-WebScraping

```



Create a virtual environment and install dependencies:



```bash

python -m venv .venv

```



Windows PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

```



\## Usage



First, collect the raw data:



```bash

python src/scraper.py

```



Next, clean the dataset:



```bash

python src/clean\_data.py

```



\## Output



\- `data/raw/books\_raw.csv` — extracted records before cleaning

\- `data/processed/books\_clean.csv` — cleaned tabular dataset

\- `data/processed/books\_clean.json` — cleaned JSON records



The scraper defaults to a maximum of five catalogue pages. The resulting record count depends on successful requests and the target site's current content.



\## Learning Outcomes



This project demonstrates HTTP requests, HTML parsing, CSS selectors, URL navigation, pagination, data cleaning, duplicate removal, file handling, and ethical scraping practices.



\## Limitations



This initial version handles static HTML. It does not implement JavaScript browser automation, database storage, or automated tests.



\## Future Improvements



\- Add Selenium for a JavaScript-rendered practice website.

\- Add SQLite storage.

\- Write unit tests for extraction and cleaning.

\- Generate a data quality report.

\- Compare scraping results from multiple permitted practice sources.



\## Ethics



Use this project only on websites whose access conditions permit your intended activity. Review the terms of use and crawling instructions, respect rate limits, and do not bypass access controls.



