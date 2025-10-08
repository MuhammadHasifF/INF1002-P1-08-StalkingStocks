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

```bash
.
├── app.py                      # Main entry script for the project.
├── src/                        # Main application source code
│   ├── __init__.py
│   ├── dashboard.py
│   ├── constants/              # Static values and domain-specific mappings
│   │   ├── __init__.py
│   │   └── sectors.py
│   ├── models/                 # Core data models and base classes
│   │   ├── __init__.py
│   │   └── base.py
│   ├── schemas/                # Data validation and dataframe schema definitions
│   │   ├── __init__.py
│   │   └── dataframe.py
│   ├── services/               # Business logic and data processing modules
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── data.py
│   │   └── finance.py
│   ├── ui/                     # Visualization and user interface components
│   │   ├── __init__.py
│   │   ├── charts.py
│   │   ├── filters.py
│   │   └── overview.py
│   └── utils/                  # General-purpose helper functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                      # Unit tests
│   ├── conftest.py
│   ├── test_core.py
│   ├── test_finance.py
│   └── test_models.py
├── docs/
├── notebook/
├── README.md
└── requirements.txt
```
