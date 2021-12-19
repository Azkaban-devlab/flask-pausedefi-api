from pausedefi_api import models
from pausedefi_api import app, db
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields
from marshmallow_sqlalchemy import SQLAlchemySchemaOpts
from marshmallow import pre_load, post_load, post_dump, EXCLUDE

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
                    if d[field] is None:
                        removed.append(field)
        else:
            for field in data:
                if data[field] is None:
                    removed.append(field)
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
    __envelope__ = {'single': 'data', 'many':'data'}
    __model__ = models.Challenge
    id = fields.Integer()
    title = fields.Str()
    content = fields.Str()
    challengers = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)
    room = ma.Nested(lambda: RoomSchema(exclude=['challenges', 'bio', 'users', 'creator']), many=False)
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=False)

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many):
        if data:
            if many:
                for i in range(0, len(data)):
                    data[i]['challengers'] = data[i]['challengers']['data']
            else:
                data['challengers'] = data['challengers']['data']
        return data


class UserSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many':'data'}
    __model__ = models.User
    password = fields.Str(load_only=True)
    email = fields.Str()
    id = fields.Integer()
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['challengers']), many=True)
    rooms = ma.Nested(lambda: RoomSchema(exclude=['challenges']), many=True)
    rooms_created = ma.Nested(lambda: RoomSchema(exclude=['challenges']), many=True)


class RoomSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    __model__ = models.Room
    id = fields.Integer()
    creator_id = fields.Integer()
    name = fields.Str()
    bio = fields.Str()
    access = fields.Str(load_only=True)
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['room'], many=True, unknown=EXCLUDE), many=True)
    users = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=False)

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many):
        if data:
            if many:
                for i in range(0, len(data)):
                    data[i]['creator'] = data[i]['creator']['data']
                    data[i]['users'] = data[i]['users']['data']
                    data[i]['challenges'] = data[i]['challenges']['data']
            else:
                data['creator'] = data['creator']['data']
                data['users'] = data['users']['data']
                data['challenges'] = data['challenges']['data']
        return data
