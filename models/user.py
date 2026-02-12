import sqlite3
from flask import g

class User:
    TABLE = "users"

    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    @staticmethod
    def get_db():
        return g.db

    @classmethod
    def create(cls, username, password):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"INSERT INTO {cls.TABLE}(username,password) VALUES(?,?)", (username, password))
        db.commit()
        return cls(username, password)

    @classmethod
    def get(cls, username):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"SELECT * FROM {cls.TABLE} WHERE username=?", (username,))
        row = c.fetchone()
        if row:
            return cls(row["username"], row["password"])
        return None
