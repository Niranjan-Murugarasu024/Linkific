# Day 18 – Regex Data Cleaning & Log Analyzer

A Python project demonstrating regular expressions for data cleaning, extraction,
format validation, and application log parsing.

## Features
- Reusable library of 28+ compiled regex patterns
- Email, Indian phone, PIN code, name, time, password, GSTIN and UUID format checks
- Extraction of emails, URLs, dates, IPv4 candidates, hashtags, mentions, order IDs and transaction IDs
- Customer CSV cleaning and normalization
- Calendar-date validation with `datetime`
- IPv4 validation with Python's `ipaddress` module
- Application log parsing and log-level summary
- Unit tests with `unittest`

## Requirements
- Python 3.10+
- pandas

## Windows PowerShell setup

```powershell
cd E:\regex_data_cleaning_day17
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

If PowerShell blocks activation, run `py -m pip install -r requirements.txt`
and use `py` for the commands below without activating the environment.

## Run the complete project

```powershell
py main.py
```

The script generates sample input data in `data/raw/`, cleans the customer
records, parses application logs, and writes reports to `data/processed/`.

## Run tests

```powershell
py -m unittest discover -s tests -v
```

## Output files
- `data/processed/cleaned_customers.csv`
- `data/processed/extracted_emails.csv`
- `data/processed/extracted_phones.csv`
- `data/processed/parsed_logs.csv`

## Project structure

```text
regex_data_cleaning_day17/
├── data/
│   ├── raw/
│   └── processed/
├── patterns/
│   └── regex_patterns.py
├── src/
│   ├── data_generator.py
│   ├── validators.py
│   ├── extractors.py
│   ├── data_cleaner.py
│   └── log_parser.py
├── tests/
│   └── test_patterns.py
├── main.py
├── requirements.txt
└── README.md
```

## Regex quick guide

| Syntax | Meaning | Example |
|---|---|---|
| `\\d` | Digit | `\\d{10}` |
| `\\D` | Non-digit | `\\D+` |
| `\\w` | Word character | `\\w+` |
| `\\W` | Non-word character | `\\W+` |
| `\\s` | Whitespace | `\\s+` |
| `.` | Any character except newline by default | `a.c` |
| `^` | Start anchor | `^Hello` |
| `$` | End anchor | `world$` |
| `*` | Zero or more | `a*` |
| `+` | One or more | `a+` |
| `?` | Zero or one | `colou?r` |
| `{n,m}` | Repetition range | `\\d{2,4}` |
| `[]` | Character class | `[A-Z]` |
| `()` | Capturing group | `(\\d{4})` |
| `|` | Alternation | `cat|dog` |
| `(?=...)` | Positive lookahead | `(?=.*\\d)` |

## Python `re` methods
- `re.search()` – find the first match anywhere in a string
- `re.match()` – attempt a match at the beginning
- `re.findall()` – return all non-overlapping matches
- `re.sub()` – replace matching text
- `re.compile()` – compile a reusable pattern
- `re.fullmatch()` – require the entire string to match

## Important limitations
Regex validates a format, not the real-world existence of a mailbox, phone
number, GST registration, or account. The sample phone validator checks a
basic Indian mobile-number format only. Calendar dates are checked with
`datetime.strptime()`, and IPv4 addresses are checked with `ipaddress`.

The sample dataset intentionally contains invalid values so the validation
reports demonstrate both accepted and rejected records.
