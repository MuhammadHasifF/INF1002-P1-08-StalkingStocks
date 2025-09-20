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
```

```powershell
# Windows 
python -m venv .venv
.venv/bin/Activate.ps1 
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Install Dependencies

```bash
python install -r requirements.txt
```

## Project Structure

```bash
.
├── README.md
├── requirements.txt
└── stalking-stocks
    ├── main.py             # entry point of our application
    ├── constants           # domain-specific constants
    │   ├── __init__.py
    │   └── sectors.py
    ├── models              # data models live here
    │   ├── __init__.py
    │   └── base.py
    ├── services            # business logic (interfacing with yfinance, APIs)
    │   ├── __init__.py
    │   ├── core.py
    │   ├── data.py
    │   └── finance.py
    └── utils               # helper functions/utilities
        ├── __init__.py
        └── helpers.py
```
