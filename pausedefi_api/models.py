from werkzeug.security import check_password_hash, generate_password_hash
from pausedefi_api import db
from datetime import datetime
from secrets import token_hex


users_challenges = db.Table(
    'users_challenges',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('challenge_id', db.Integer, db.ForeignKey('challenge.id')),
)

users_rooms = db.Table(
    'users_rooms',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f"User('{self.email}')"

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False, unique=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    challengers = db.relationship('User', secondary=users_challenges, backref=db.backref('challenges', lazy='dynamic'))

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref=db.backref('challenges'))

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('challenges_created'))

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def __repr__(self):
        return f"Challenge('{self.title}')"


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=False)
    bio = db.Column(db.Text, nullable=True, unique=False)
    access = db.Column(db.String(255), nullable=False, unique=True, default=token_hex(5))

    users = db.relationship('User', secondary=users_rooms, backref=db.backref('rooms', lazy='dynamic'))

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('rooms_created'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Room('{self.name}')"