import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv('LOG_DB_PATH', 'processing_logs.db')

# Initialize DB and table
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY,
    uid TEXT,
    sender TEXT,
    city TEXT,
    timestamp TEXT,
    attachments TEXT,
    status TEXT
)
''')
conn.commit()


def log_event(uid, sender, city, attachments, status):
    ts = datetime.utcnow().isoformat() + 'Z'
    cur.execute(
        'INSERT INTO logs (uid,sender,city,timestamp,attachments,status) VALUES (?,?,?,?,?,?)',
        (uid.decode() if isinstance(uid, bytes) else uid,
         sender,
         city,
         ts,
         ','.join(attachments),
         status)
    )
    conn.commit()


def fetch_logs(limit=50):
    cur.execute('SELECT uid,sender,city,timestamp,attachments,status FROM logs ORDER BY id DESC LIMIT ?', (limit,))
    return cur.fetchall()