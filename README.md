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

├── src/                        
│   ├── constants/             
│   ├── models/                
│   ├── services/              
│   ├── ui/                     
│   └── utils/                  
├── tests/                      
│    ├── conftest.py
│    ├── test_core.py
│    ├── test_finance.py
│    ├── test_edge_case.py
│    └── test_models.py

