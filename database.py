import sqlite3

DB = "chat.db"

def connect():
    return sqlite3.connect(DB, check_same_thread=False)

db = connect()
c = db.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  phone TEXT,
  bio TEXT,
  photo TEXT,
  online INTEGER DEFAULT 0
)
""")

# MESSAGES
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender TEXT,
  receiver TEXT,
  room TEXT,
  text TEXT,
  type TEXT,
  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# LIKES
c.execute("""
CREATE TABLE IF NOT EXISTS likes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  msg_id INTEGER,
  username TEXT
)
""")

# COMMENTS
c.execute("""
CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  msg_id INTEGER,
  username TEXT,
  text TEXT
)
""")

# GROUPS / CHANNELS
c.execute("""
CREATE TABLE IF NOT EXISTS rooms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE,
  admin TEXT,
  type TEXT,
  comments_locked INTEGER DEFAULT 0
)
""")

db.commit()
