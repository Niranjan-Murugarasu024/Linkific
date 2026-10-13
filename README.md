# Python Data Engineering Practice Project

This repository contains a collection of beginner-to-intermediate Python exercises covering core Python concepts and common data engineering tasks. The project was reviewed and updated to fix broken file paths and runtime issues so each script runs correctly from the project root.

## Project overview

The scripts are organized in sequence from basic Python fundamentals to practical file and data-processing workflows:

1. Variables and basic data types
2. Data structures
3. Comprehensions
4. Functions and lambda expressions
5. Exception handling
6. Context managers
7. Modules and path handling
8. Text file processing
9. CSV processing
10. JSON processing
11. Excel report generation
12. Pathlib usage
13. Bulk CSV aggregation
14. API requests
15. Log processing

## Folder structure

```text
Day-1/
├── 01_Variables.py
├── 02_data_structures.py
├── 03_comprehensions.py
├── 04_functions.py
├── 05_exceptionalhandling.py
├── 06_contextmanagers.py
├── 07_modules.py
├── 08_textfile.py
├── 09_csvfile.py
├── 10_jsonfile.py
├── 11_excelfile.py
├── 12_pathlib.py
├── 13_bulkprocessing.py
├── 14_apirequest.py
├── 15_logprocessing.py
├── data/
│   ├── config.json
│   ├── feb_sales.csv
│   ├── jan_sales.csv
│   ├── sample.txt
│   ├── output/
│   │   ├── all_sales.csv
│   │   └── sales_report.xlsx
│   └── processed/
│       ├── config_copy.json
│       └── sales_cleaned.csv
└── README.md
```

## Requirements

Install the required Python packages if they are not already available:

```bash
pip install pandas openpyxl requests
```

## Usage

Run any script directly from the repository root:

```bash
python 01_Variables.py
python 08_textfile.py
python 09_csvfile.py
python 11_excelfile.py
python 14_apirequest.py
```

## What was fixed

The main issue in the project was incorrect path resolution. Several scripts used `Path(__file__).resolve().parent.parent`, which pointed to the parent directory instead of the project root. That caused file-not-found errors when the scripts attempted to read data under the `data/` folder.

The scripts were updated to use the project directory correctly and to fall back gracefully when the expected `data/raw` structure is absent. This makes the exercises work with the current repository layout.

## Notes

- `09_csvfile.py` reads the sales data and writes a cleaned CSV into `data/processed/`.
- `10_jsonfile.py` loads the configuration file and writes a processed copy.
- `11_excelfile.py` creates a sales report workbook in `data/output/`.
- `13_bulkprocessing.py` combines sales CSV files into a unified output file.
- `14_apirequest.py` fetches public sample data from JSONPlaceholder.
- `15_logprocessing.py` counts log levels found in the sample log file.

## License

This project is intended for educational and practice use.
