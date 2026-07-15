import sqlite3, os

db = os.path.abspath('localhub.db')
print("DB:", db)
conn = sqlite3.connect(db)
cur = conn.cursor()

cols = [r[1] for r in cur.execute("PRAGMA table_info(posts)").fetchall()]
print("existing posts columns:", cols)

if 'category' not in cols:
    print("Adding column: category")
    cur.execute("ALTER TABLE posts ADD COLUMN category TEXT")
else:
    print("category already exists")

if 'edit_password' not in cols:
    print("Adding column: edit_password")
    cur.execute("ALTER TABLE posts ADD COLUMN edit_password TEXT")
else:
    print("edit_password already exists")

conn.commit()
conn.close()
print("Migration done")