from pausedefi_api import models
from pausedefi_api import app, db
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields
from marshmallow_sqlalchemy import SQLAlchemySchemaOpts
from marshmallow import pre_load, post_load, post_dump

ma = Marshmallow(app)


class BaseOpts(SQLAlchemySchemaOpts):
    def __init__(self, meta, ordered=False):
        if not hasattr(meta, "sqla_session"):
            meta.sqla_session = db.Session
        super(BaseOpts, self).__init__(meta, ordered=ordered)


class BaseSchema(ma.SQLAlchemySchema):
    OPTIONS_CLASS = BaseOpts
    __envelope__ = {"single": None, "many": None}

    def get_envelope_key(self, many):
        """Helper to get the envelope key."""
        key = self.__envelope__["many"] if many else self.__envelope__["single"]
        assert key is not None, "Envelope key undefined"
        return key

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return data[key]

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return {key: data}

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class ChallengeSchema(ma.SQLAlchemyAutoSchema):
    challengers = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)
    room = ma.Nested(lambda: RoomSchema(exclude=['challenges', 'bio', 'users', 'creator']), many=False)
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=False)

    class Meta:
        model = models.Challenge


class UserSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many':'data'}
    password = fields.Str(load_only=True)
    email = fields.Str()
    id = fields.Integer()
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['challengers']), many=True)
    rooms = ma.Nested(lambda: RoomSchema(exclude=['challenges']), many=True)
    rooms_created = ma.Nested(lambda: RoomSchema(exclude=['challenges']), many=True)

    class Meta:
        model = models.User


class RoomSchema(BaseSchema):
    __envelope__ = {'single': 'data', 'many': 'data'}
    id = fields.Integer()
    creator_id = fields.Integer()
    name = fields.Str()
    bio = fields.Str()
    access = fields.Str(load_only=True)
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['room']), many=True)
    users = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=False)

    @post_dump(pass_many=True)
    def unwrap_envelope(self, data, many):
        if data:
            if many:
                for i in range(0, len(data)):
                    data[i]['creator'] = data[i]['creator']['data']
                    data[i]['users'] = data[i]['users']['data']
            else:
                data['creator'] = data['creator']['data']
                data['users'] = data['users']['data']
        return data

    class Meta:
        model = models.Room