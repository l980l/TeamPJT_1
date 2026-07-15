import json
import os
from app import models
from app.database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_all():
    session = SessionLocal()
    try:
        for fname in os.listdir(DATA_DIR):
            if not fname.lower().endswith('.json'):
                continue
            path = os.path.join(DATA_DIR, fname)
            with open(path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                items = doc.get('items', [])
                for it in items:
                    # normalize fields
                    data = dict(it)
                    # convert mapx/mapy to floats when possible
                    try:
                        data['mapx'] = float(data.get('mapx')) if data.get('mapx') else None
                    except Exception:
                        data['mapx'] = None
                    try:
                        data['mapy'] = float(data.get('mapy')) if data.get('mapy') else None
                    except Exception:
                        data['mapy'] = None

                    # set region/contentType if present at top level
                    if 'region' in doc:
                        data['region'] = doc.get('region')
                    if 'contentType' in doc:
                        data['contentType'] = doc.get('contentType')

                    obj = models.Item(**data)
                    session.merge(obj)
        session.commit()
    finally:
        session.close()


if __name__ == '__main__':
    load_all()
    print('Seed complete')
