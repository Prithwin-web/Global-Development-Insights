# GLOBAL DEVELOPMENT INSIGHTS — Installation & Usage Guide

---

## 1. FOLDER STRUCTURE

```
project/
│
├── app.py                          ← Main Flask application
├── requirements.txt                ← Python dependencies
│
├── templates/
│   ├── base.html                   ← Sidebar + topnav layout
│   ├── index.html                  ← Home / dashboard page
│   ├── country.html                ← Country analysis page
│   └── error.html                  ← Error / not found page
│
├── static/
│   ├── css/
│   │   └── style.css               ← Full dashboard stylesheet
│   └── charts/                     ← Auto-generated PNG charts
│
└── utils/
    ├── __init__.py
    ├── data_loader.py              ← CSV loading + caching
    ├── chart_generator.py          ← Matplotlib chart generation
    └── country_validator.py        ← Fuzzy country name matching
```

---

## 2. CSV FILE PLACEMENT

Place your two CSV files at the exact paths below, OR update the
paths in `utils/data_loader.py`:

```
E:\2nd_Sem\AIML\Project\Dataset\Preprocessed\Final_Clustered_Dataset.csv
E:\2nd_Sem\AIML\Project\Dataset\Preprocessed\Future_Development_Dataset_2025_2040.csv
```

### Required columns

**Final_Clustered_Dataset.csv**
```
Country Name, Year, GDP, Inflation, Internet_Users,
Life_Expectancy, Literacy_Rate, Poverty, Unemployment,
Development_Score, Development_Level
```

**Future_Development_Dataset_2025_2040.csv**
```
Country Name, Year, GDP_Per_Capita, Development_Score, Development_Level
```

---

## 3. VIRTUAL ENVIRONMENT SETUP

### Windows (Command Prompt)
```cmd
cd E:\2nd_Sem\AIML\Project
python -m venv venv
venv\Scripts\activate
```

### Windows (PowerShell)
```powershell
cd E:\2nd_Sem\AIML\Project
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
cd ~/path/to/project
python3 -m venv venv
source venv/bin/activate
```

---

## 4. DEPENDENCY INSTALLATION

```bash
pip install -r requirements.txt
```

Installs: Flask 3.0, Pandas 2.2, Matplotlib 3.9, NumPy 1.26

---

## 5. RUNNING THE APPLICATION

```bash
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Open your browser at: **http://localhost:5000**

---

## 6. USING THE DASHBOARD

1. **Home Page** — Shows global stats (total countries, avg score, distribution)
2. **Search** — Type any country name in the hero search bar or top nav
3. **Country Dashboard** — Full analysis with:
   - Analytics cards (GDP, Life Expectancy, Literacy, Internet Users…)
   - Current development status (color-coded badge)
   - Single indicator chart selector → Generate Chart
   - Multi-indicator comparison (check multiple boxes) → Compare
   - Forecast chart (GDP Per Capita or Dev Score, 2025–2040)
   - Future Year dropdown → see projected status for any year 2025–2040

---

## 7. CHANGING CSV PATHS

If your CSVs are in a different location, edit `utils/data_loader.py`:

```python
HISTORICAL_CSV = r'C:\your\path\Final_Clustered_Dataset.csv'
FUTURE_CSV     = r'C:\your\path\Future_Development_Dataset_2025_2040.csv'
```

Or set environment variables before running:

```cmd
set HISTORICAL_CSV=C:\path\to\Final_Clustered_Dataset.csv
set FUTURE_CSV=C:\path\to\Future_Development_Dataset_2025_2040.csv
python app.py
```

---

## 8. PRODUCTION DEPLOYMENT (Waitress / Gunicorn)

### Windows (Waitress)
```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Linux / macOS (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 9. TROUBLESHOOTING

| Problem | Fix |
|---|---|
| `FileNotFoundError: Historical CSV not found` | Update path in `utils/data_loader.py` |
| `Missing required column: Development_Level` | Check CSV column names match exactly |
| Charts not showing | Ensure `static/charts/` folder exists (auto-created) |
| Port 5000 already in use | Change port: `app.run(port=5001)` in `app.py` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in venv |
| Country not found | Try partial name (e.g. "United" for "United States") |
| Blank page on POST | Check Flask debug console for traceback |

---

## 10. FEATURES SUMMARY

| Feature | Method | Technology |
|---|---|---|
| Home dashboard | GET `/` | Flask + Jinja2 |
| Country search | POST `/search` | HTML Form |
| Country analysis | GET/POST `/country/<name>` | Flask route |
| Historical chart | POST (form) | Matplotlib → PNG |
| Multi-indicator chart | POST (checkboxes) | Matplotlib → PNG |
| Forecast chart | POST (select) | Matplotlib → PNG |
| Future year index | POST (dropdown) | Pandas filter |
| Error handling | All routes | try/except + error.html |
| Country fuzzy match | `validate_country()` | difflib |

---

*GLOBAL DEVELOPMENT INSIGHTS · AIML Project · 2nd Semester*
