from pausedefi_api import models
from pausedefi_api import app, db
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields
from marshmallow_sqlalchemy import SQLAlchemySchemaOpts
from marshmallow import pre_load, post_load, post_dump, EXCLUDE
from sqlalchemy import and_

from pausedefi_api.models import ChallengeUsers, RoomUsers

ma = Marshmallow(app)


class BaseOpts(SQLAlchemySchemaOpts):
    def __init__(self, meta, ordered=False):
        if not hasattr(meta, "sqla_session"):
            meta.sqla_session = db.Session
            meta.load_instance = True
            meta.include_relationships = True
            meta.partial = True
            meta.unknown = EXCLUDE
        super(BaseOpts, self).__init__(meta, ordered=ordered)


class BaseSchema(ma.SQLAlchemySchema):
    OPTIONS_CLASS = BaseOpts
    __envelope__ = {"single": None, "many": None}
    __model__ = None

    def get_envelope_key(self, many):
        """Helper to get the envelope key."""
        key = self.__envelope__["many"] if many else self.__envelope__["single"]
        assert key is not None, "Envelope key undefined"
        return key

    @pre_load(pass_many=True)
    def remove_none(self, data, many, **kwargs):
        removed = []
        if many:
            for d in data:
                for field in d:
                    try:
                        if d[field] is None:
                            removed.append(field)
                    except:
                        pass
        else:
            for field in data:
                try:
                    if data[field] is None:
                        removed.append(field)
                except:
                    pass
        if many:
            for item in removed:
                for field in data:
                    if item in field:
                        field.pop(item)
        else:
            for item in removed:
                if item in data:
                    data.pop(item)
        return data

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return {key: data}

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class ChallengeSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    __model__ = models.Challenge
    id = fields.Integer()
    title = fields.Str()
    content = fields.Str()
    state = fields.Str()
    points = fields.Integer()
    date_posted = fields.DateTime()
    challengers = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created'], many=True))
    room = ma.Nested(lambda: RoomSchema(exclude=['challenges', 'bio', 'users', 'creator'], many=False))
    room_id = fields.Integer()
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created'], many=False))
    creator_id = fields.Integer()

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        user_id = self.context.get('user_id')
        if data:
            if many:
                for i in range(0, len(data)):
                    if user_id is not None:
                        data[i]['state'] = str(ChallengeUsers.query.filter(and_(ChallengeUsers.user_id == user_id, ChallengeUsers.challenge_id == data[i]['id'])).first().state)
                    if 'room' in data[i]:
                        data[i]['room'] = data[i]['room']['data']
                    if 'challengers' in data[i]:
                        data[i]['challengers'] = data[i]['challengers']['data']
                    if 'creator' in data[i]:
                        data[i]['creator'] = data[i]['creator']['data']
            else:
                if user_id is not None:
                    data['state'] = str(ChallengeUsers.query.filter(and_(ChallengeUsers.user_id == user_id, ChallengeUsers.challenge_id == data['id'])).first().state)
                if 'room' in data:
                    data['room'] = data['room']['data']
                if 'challengers' in data:
                    data['challengers'] = data['challengers']['data']
                if 'creator' in data:
                    data['creator'] = data['creator']['data']
        return data


class UserSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    __model__ = models.User
    password = fields.Str(load_only=True)
    email = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    id = fields.Integer()
    points = fields.Integer()
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['challengers'], many=True))
    rooms = ma.Nested(lambda: RoomSchema(exclude=['challenges'], many=True))
    rooms_created = ma.Nested(lambda: RoomSchema(exclude=['challenges'], many=True))

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        room_id = self.context.get('room_id')
        if data:
            if many:
                for i in range(0, len(data)):
                    if room_id is not None:
                        data[i]['points'] = str(RoomUsers.query.filter(and_(RoomUsers.room_id == room_id, RoomUsers.user_id == data[i]['id'])).first().points)
                    if 'rooms' in data[i]:
                        data[i]['rooms'] = data[i]['rooms']['data']
                    if 'challenges' in data[i]:
                        data[i]['challenges'] = data[i]['challenges']['data']
            else:
                if room_id is not None:
                    data['points'] = str(RoomUsers.query.filter(and_(RoomUsers.room_id == room_id, RoomUsers.user_id == data['id'])).first().points)
                if 'rooms' in data:
                    data['rooms'] = data['rooms']['data']
                if 'challenges' in data:
                    data['challenges'] = data['challenges']['data']
        return data


class RoomSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    __model__ = models.Room
    id = fields.Integer()
    creator_id = fields.Integer()
    name = fields.Str()
    bio = fields.Str()
    access = fields.Str(load_only=True)
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['room'], many=True, unknown=EXCLUDE))
    users = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created'], many=True))
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created'], many=False))

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many):
        if data:
            if many:
                for i in range(0, len(data)):
                    if 'creator' in data[i]:
                        data[i]['creator'] = data[i]['creator']['data']
                    if 'users' in data[i]:
                        data[i]['users'] = data[i]['users']['data']
                    if 'challenges' in data[i]:
                        data[i]['challenges'] = data[i]['challenges']['data']
            else:
                if 'creator' in data:
                    data['creator'] = data['creator']['data']
                if 'users' in data:
                    data['users'] = data['users']['data']
                if 'challenges' in data:
                    data['challenges'] = data['challenges']['data']
        return data


class ChallengeUsersSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    __model__ = models.ChallengeUsers
    challenge_id = fields.Integer()
    user_id = fields.Str()
    challenge = ma.Nested(lambda: ChallengeSchema())
    challenger = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']))
    state = fields.Str()

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many):
        if data:
            if many:
                for i in range(0, len(data)):
                    if 'challenge' in data[i]:
                        data[i]['challenge'] = data[i]['challenge']['data']
                    if 'challenger' in data[i]:
                        data[i]['challenger'] = data[i]['challenger']['data']
            else:
                if 'challenge' in data:
                    data['challenge'] = data['challenge']['data']
                if 'challenger' in data:
                    data['challenger'] = data['challenger']['data']
        return data


class RoomUsersSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    __model__ = models.RoomUsers
    room_id = fields.Integer()
    user_id = fields.Str()
    room = ma.Nested(lambda: RoomSchema())
    user = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']))
    points = fields.Integer()

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many):
        if data:
            if many:
                for i in range(0, len(data)):
                    if 'room' in data[i]:
                        data[i]['room'] = data[i]['room']['data']
                    if 'user' in data[i]:
                        data[i]['user'] = data[i]['user']['data']
            else:
                if 'room' in data:
                    data['room'] = data['room']['data']
                if 'user' in data:
                    data['user'] = data['user']['data']
        return data
