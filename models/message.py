from flask import g

class Message:
    TABLE = "messages"

    def __init__(self, sender, receiver, text, type="text", media_url=None, status="sent", id=None):
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.type = type
        self.media_url = media_url
        self.status = status
        self.id = id

    @staticmethod
    def get_db():
        return g.db

    @classmethod
    def create(cls, sender, receiver, text, type="text", media_url=None, status="sent"):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"INSERT INTO {cls.TABLE}(sender,receiver,text,type,media_url,status) VALUES(?,?,?,?,?,?)",
                  (sender, receiver, text, type, media_url, status))
        db.commit()
        return cls(sender, receiver, text, type, media_url, status, c.lastrowid)

    @classmethod
    def get_conversation(cls, user1, user2):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"""
            SELECT * FROM {cls.TABLE}
            WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
            ORDER BY id ASC
        """, (user1, user2, user2, user1))
        return [cls(row["sender"], row["receiver"], row["text"], row["type"], row["media_url"], row["status"], row["id"])
                for row in c.fetchall()]

    @classmethod
    def mark_seen(cls, sender, receiver):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"UPDATE {cls.TABLE} SET status='seen' WHERE sender=? AND receiver=?", (sender, receiver))
        db.commit()

    @classmethod
    def delete(cls, sender, text):
        db = cls.get_db()
        c = db.cursor()
        c.execute(f"DELETE FROM {cls.TABLE} WHERE sender=? AND text=?", (sender, text))
        db.commit()
