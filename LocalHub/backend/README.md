# LocalHub backend

FastAPI backend with SQLAlchemy + SQLite for LocalHub.

Run locally:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Place source JSON files under `data/` and run `seed.py` to load.
