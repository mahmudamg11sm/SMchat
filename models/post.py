from flask import g

class Post:
    TABLE = "posts"

    def __init__(self, user, content, id=None):
        self.user = user
        self.content = content
        self.id = id

    @staticmethod
    def get_db():
        return g.db

    @classmethod
    def create(cls, user, content):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"INSERT INTO {cls.TABLE}(user,content) VALUES(?,?)", (user, content))
        db.commit()
        return cls(user, content, c.lastrowid)

    @classmethod
    def all(cls):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"SELECT * FROM {cls.TABLE} ORDER BY id DESC")
        return [cls(row["user"], row["content"], row["id"]) for row in c.fetchall()]
