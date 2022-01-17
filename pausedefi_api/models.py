from werkzeug.security import check_password_hash, generate_password_hash
from pausedefi_api import db
from datetime import datetime
import uuid
import enum


class ChallengeState(enum.Enum):
    in_progress = 'in_progress'
    succeed = 'succeed'
    failed = 'failed'
    rejected = 'rejected'

    def __str__(self):
        return self.name


class ChallengeUsers(db.Model):
    __tablename__ = 'challenges_users'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), primary_key=True)
    state = db.Column(db.Enum(ChallengeState), default=ChallengeState.in_progress)

    user = db.relationship("User", backref=db.backref("challenge_users", cascade="all, delete-orphan"))
    challenge = db.relationship("Challenge", backref=db.backref("challenge_users", cascade="all, delete-orphan"))

    def __init__(self, challenge=None, challenger=None):
        self.user = challenger
        self.challenge = challenge


class RoomUsers(db.Model):
    __tablename__ = 'rooms_users'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    points = db.Column(db.Integer, default=0)

    user = db.relationship("User", backref=db.backref("room_users", cascade="all, delete-orphan"))
    room = db.relationship("Room", backref=db.backref("room_users", cascade="all, delete-orphan"))

    def __init__(self, room=None, user=None):
        self.user = user
        self.room = room


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False, unique=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref=db.backref('challenges'))
    challengers = db.relationship('User', secondary="challenges_users", viewonly=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('challenges_created'))
    points = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Challenge('{self.title}')"

    def add_users(self, items):
        for challenger in items:
            self.challenge_users.append(ChallengeUsers(challenge=self, challenger=challenger))

    def update_state(self, state, user_id):
        for defi in self.challenge_users:
            if defi.user_id == user_id:
                defi.state = state


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    challenges = db.relationship("Challenge", secondary="challenges_users", viewonly=True)
    rooms = db.relationship("Room", secondary="rooms_users", viewonly=True)

    def __init__(self, **data):
        self.email = data['email']
        if 'password' in data:
            self.password = generate_password_hash(data['password'])
        self.first_name = data['first_name']
        self.last_name = data['last_name']

    def __repr__(self):
        return f"User('{self.email, self.id}')"

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=False)
    bio = db.Column(db.Text, nullable=True, unique=False)
    access = db.Column(db.String(255), nullable=False, unique=True)

    users = db.relationship("User", secondary="rooms_users", viewonly=True)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref=db.backref('rooms_created'))

    def __init__(self, name, challenges):
        self.name = name,
        self.challenges = challenges
        self.access = uuid.uuid4().hex[:5]

    def __repr__(self):
        return f"Room('{self.name}')"

    def add_users(self, users):
        for user in users:
            self.room_users.append(RoomUsers(room=self, user=user))

    def update_point(self, point, user_id):
        for entity in self.room_users:
            if entity.user_id == user_id:
                entity.points += point
