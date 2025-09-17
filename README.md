# 📘 README Overview

## Purpose of This README

This README serves as the central documentation for the **Stalking Stocks** project, developed for the INF1002 Programming Fundamentals module. It provides:

- A clear introduction to the project and its goals  
- Setup and usage instructions for contributors and users  
- A detailed breakdown of features and architecture  
- Task allocation and development phases  
- References and resources used throughout the project

---

## 🛠️ Setup Guide

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

---

## 📊 Project Proposal  
**Course:** INF1002 Programming Fundamentals  
**Team ID:** P1-8  

### 1. Project Title  
**Stalking Stocks**

### 2. Team List

| Name                            | Student ID | Email                                      |
|---------------------------------|------------|--------------------------------------------|
| Mohammed Aamir                  | 2500933    | 2500933@sit.singaporetech.edu.sg          |
| Muhammad Hasif Bin Mohd Faisal | 2500619    | 2500619@sit.singaporetech.edu.sg          |
| Timothy Chia Kai Lun           | 2501530    | 2501530@sit.singaporetech.edu.sg          |
| Low Gin Lim                    | 2501267    | 2501267@sit.singaporetech.edu.sg          |
| Dalton Chng Cheng Hao          | 2504003    | 2504003@sit.singaporetech.edu.sg          |

### 3. Project Description  
A comprehensive stock-analysis web application using pre-loaded financial data from multiple sectors (technology, finance, healthcare, consumer goods, energy) spanning the past 2–3 years.

### 4. Problem Statement  
Novice investors often struggle with the overwhelming complexity of financial data. *Stalking Stocks* simplifies this experience through intuitive visuals and data-driven insights, helping users learn and make informed decisions in a risk-free environment.

### 5. Objectives

1. Implement modular Python functions for technical indicators and performance metrics using sliding-window and dictionary-based algorithms.  
2. Develop a responsive Streamlit web interface with interactive charts and dashboards.  
3. Validate analytical outputs against trusted sources (e.g., `pandas.rolling().mean()`) with ≥5 test cases per core function.  
4. Maintain clear logic, modular code, and strong team coordination throughout all phases.

### 6. Features

- Browse stocks by company or sector  
- View interactive price charts with technical indicators (e.g., SMAs)  
- Analyze performance metrics: daily returns, trend runs, max profit  
- Market overview dashboard: top/worst performers, volatility, trend streaks  
- Compare up to four stocks simultaneously  
- Sector performance comparisons across time periods  
- “Market Moments” view: reactions to Fed announcements, earnings, corrections  
- All data pre-processed and embedded for instant analysis

### 7. Initial Task Allocation

| Phase | Member(s) | Responsibilities | Deliverables |
|-------|-----------|------------------|--------------|
| **1. Project Architecture & Methodology** | All Members | Define modular structure, set up repo layout, design module/function list, choose programming paradigm, style guide & documentation practices | Initial README |
| **2. Data Acquisition & Preprocessing** | Aamir, Dalton | Retrieve data via `yfinance`, clean and transform data, handle missing values, standardize formats, flag outliers, generate quality reports | Analysis library, algorithm docs, test summary |
| **3. Core Algorithm Development** | Hasif, Gin | Implement SMAs, trend detection, daily returns, volatility, max-profit algorithm (multi-transaction), unit tests and edge case handling | Test summary |
| **4. Full-Stack Interface & Data Services** | Timothy, Gin, Dalton | Streamlit dashboard with Plotly charts, interactive selectors (tickers, sectors, date ranges), multi-stock comparison view, responsive UI and modular service layer | App interface, API docs, UI notes |
| **5. Integration, Testing & Deployment** | All Members | Integrate backend/frontend, validate outputs vs. pandas/manual, debug performance issues | Final test report, usage docs |

### 8. References

- [Flask Documentation](https://flask.palletsprojects.com)  
- [LeetCode – Best Time to Buy and Sell Stock II](https://leetcode.com)  
- [pandas.DataFrame.rolling API](https://pandas.pydata.org)  
- [PEP 8 – Python Style Guide](https://peps.python.org/pep-0008/)  
- [Plotly Python Graphing Library](https://plotly.com/python/)  
- [Streamlit Documentation](https://streamlit.io)  
- [yfinance on PyPI](https://pypi.org/project/yfinance/)  
- [Responsive Design Principles – Google](https://developers.google.com/web/fundamentals/design-and-ux/responsive)  
- [IEEE 829-2019 – Software Test Documentation](https://ieeexplore.ieee.org/document/829)
