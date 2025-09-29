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
streamlit run app.py
```

### Testing

```bash
# run all tests
python -m pytest

# run tests in a specific file
python -m pytest path/to/your_test_file.py

# run tests by keyword
python -m pytest -k "keyword_to_match"

# run test on specific function
python -m pytest path/to/your_test_file.py::test_function_name

# to get verbose output during tests
python -m pytest -v
```

## Project Structure

```markdown
.
├── app.py                     # Main entry script for the project.
├── app
│   ├── dashboard.py           # Main dashboard logic and Streamlit interface functions
│   ├── __init__.py
│   ├── constants
│   │   ├── __init__.py
│   │   └── sectors.py         # Contains sector-related constants and mappings
│   ├── models
│   │   ├── __init__.py
│   │   └── base.py            # Core data models (e.g., Industry, Sector, Ticker)
│   ├── schemas
│   │   ├── __init__.py
│   │   └── dataframe.py       # Schema definitions for tabular data structures
│   ├── services
│   │   ├── __init__.py
│   │   ├── core.py            # Core business logic functions (e.g., compute_max_profit, compute_sdr)
│   │   ├── data.py            # Data handling functions (e.g., load, transform, save)
│   │   └── finance.py         # Finance-related computations and analytics
│   └── utils
│       ├── __init__.py
│       └── helpers.py         # General helper functions (e.g., timers, logging, small utilities)
├── docs
│   ├── Project Proposal.pdf
│   ├── Project Specifications and Rubrics.pdf
│   └── System Design.pdf
├── notebook
│   ├── algorithms.ipynb
│   ├── data.ipynb
│   ├── guide.ipynb
│   └── programming notes.ipynb
├── README.md
├── requirements.txt
└── tests
    ├── conftest.py
    ├── test_core.py
    ├── test_finance.py
    └── test_models.py

10 directories, 28 files
```
