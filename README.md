# Stalking Stocks

A financial analysis application for beginner investors.

## Setup Guide

### Prerequisites 

- Python 3.9+ installed  
- `pip` or `conda` for package management  

### Create and Activate a Virtual Environment

```bash
# Linux/macOS 
python3 -m venv .venv
source .venv/bin/activate 

# Windows 
python -m venv .venv
.venv/bin/Activate.ps1 

# To deactive environment
deactivate
```

### Install Dependencies

```bash
python install -r requirements.txt
```

### Starting the App

```bash
streamlit run app/main.py
```

### Testing

```bash
# run all tests
pytest

# run tests in a specific file
pytest path/to/your_test_file.py

# run tests by keyword
pytest -k "keyword_to_match"

# run test on specific function
pytest path/to/your_test_file.py::test_function_name

# to get verbose output during tests
pytest -v
```

## Project Structure

```bash
.
├── app
│   ├── main.py             # entry point of our application
│   ├── constants           # domain-specific constants
│   │   ├── __init__.py
│   │   └── sectors.py
│   ├── models              # data models live here
│   │   ├── __init__.py
│   │   └── base.py
│   ├── schemas             # dataframe models live here
│   │   ├── __init__.py
│   │   └── dataframes.py
│   ├── services            # business logic (interfacing with yfinance, APIs)
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── data.py
│   │   └── finance.py
│   └── utils               # helper functions/utilities
│       ├── __init__.py
│       └── helpers.py
├── tests                   # tests go here
│   └── ...
├── docs
│   ├── Project Proposal.pdf
│   ├── Project Specifications and Rubrics.pdf
│   └── System Design.pdf
├── README.md
└── requirements.txt
```
