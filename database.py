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
  bio TEXT,
  profile_pic TEXT
)
""")

# CHANNELS
c.execute("""
CREATE TABLE IF NOT EXISTS channels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE,
  admin TEXT
)
""")

# MEMBERS
c.execute("""
CREATE TABLE IF NOT EXISTS members (
  user TEXT,
  channel TEXT,
  PRIMARY KEY(user, channel)
)
""")

# MESSAGES
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender TEXT,
  channel TEXT,
  text TEXT,
  type TEXT,
  media_url TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# COMMENTS
c.execute("""
CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id INTEGER,
  commenter TEXT,
  text TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# LIKES
c.execute("""
CREATE TABLE IF NOT EXISTS likes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id INTEGER,
  user TEXT
)
""")

db.commit()
