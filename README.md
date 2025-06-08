# uiuc-rooms

Small project to view room availability for the UIUC. 

# Requirements

To install requirements, please run:
```bash
pip install -r requirements.txt
```

# Cleaning

The initial CSV produced is pretty noisy. In order to clean it, we have 
added the `clean.py`:

```bash
python clean.py --in SP25_UIUC_courses.csv --out courses_clean.csv
```

- `in`: parameter where you specify the path to initial CSV
- `out`: parameter where you specify the name of the CSV you want

# Running the project

To run the project, run:
```
streamlit run app.py 
```