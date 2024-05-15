# UMGC Catalog Project using H2O Wave

## Overview
The purpose behind this project is to create a self-serve registration app that follows the UMGC course catalog. We chose H2O Wave (http://wave.h2o.ai) as the UI since 

1. it is written in Python so HTML, Javascript, etc. skills are not necessarily needed, 
2. it is more stable in production environments than competing choices such as Streamlit (e.g., AT&T has hundreds of H2O Wave apps in production within their corporate environment),
3. authorship in Python enables the use of many Python machine learning and AI libraries that are not directly available in D3, for instance.

## Files

The files required by the Wave app include:

- `app.py`
- `cards.py`
- `templates.py`
- `utils.py`
- `class_d3.js`
- `UMGC.db`


## Appendix
### Notes on UMGC Online Menus

- The Healthcare Administration MS degree shows up online but not in the catalog
- Accounting graduate certificate shows up online but not in catalog