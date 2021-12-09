from pausedefi_api import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User('{self.email}')"


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False, unique=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return f"Challenge('{self.email}')"