from datetime import datetime
from app import db

class Reaction(db.Model):
    __tablename__ = "reactions"

    id = db.Column(db.Integer, primary_key=True)

    message_id = db.Column(db.Integer, nullable=False)

    sender = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(100), nullable=False)

    emoji = db.Column(db.String(10), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent duplicate reaction from same user on same message
    __table_args__ = (
        db.UniqueConstraint("message_id", "sender", name="unique_user_reaction"),
    )

    def __repr__(self):
        return f"<Reaction {self.emoji} by {self.sender}>"
