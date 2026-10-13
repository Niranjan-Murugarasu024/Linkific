# Day-2 API Data Collection Project

This project fetches data from public APIs, saves the raw JSON responses, and converts the retrieved records into CSV files for easier analysis.

## Project Overview

The script performs a simple Extract-Transform-Load (ETL) workflow:

- Extracts JSON data from online APIs
- Saves the original response as raw JSON files
- Normalizes the response into a tabular format
- Exports the processed data as CSV files

## Files

- `api_client.py` – contains the reusable HTTP helper function for fetching API data
- `main.py` – main script that calls the API endpoints, saves JSON, and exports CSV
- `data/raw/` – stores raw API responses
- `data/processed/` – stores cleaned/processed CSV files
- `requirements.txt` – Python dependencies

## APIs Used

The project currently fetches data from:

- JSONPlaceholder Posts API
- DummyJSON Products API
- JSONPlaceholder Users API

## How It Works

1. The script defines a dictionary of API URLs in `main.py`.
2. It loops through each endpoint and calls `get_data()` from `api_client.py`.
3. The API response is saved to `data/raw/<name>.json`.
4. If the response contains a list of records, it is normalized into a pandas DataFrame.
5. The DataFrame is exported to `data/processed/<name>.csv`.

## Requirements

- Python 3.x
- `requests`
- `pandas`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project

From the project folder, run:

```bash
python main.py
```

This will fetch all configured datasets and save them in the `data/` folders.

## Output Structure

```text
Day-2/
├── api_client.py
├── main.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   │   ├── posts.json
│   │   ├── products.json
│   │   └── users.json
│   └── processed/
│       ├── posts.csv
│       ├── products.csv
│       └── users.csv
```

## Notes

- The script creates the output folders automatically if they do not exist.
- Errors from failed API requests are caught and printed to the console without stopping the whole script.

## GitHub Push Instructions

If you want to push this folder to a GitHub repository, use the following commands:

```bash
git init
git add .
git commit -m "Initial commit for Day-2 API data project"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## License

This project is provided for learning and demonstration purposes.
