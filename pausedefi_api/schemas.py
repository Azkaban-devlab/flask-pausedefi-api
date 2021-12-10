from pausedefi_api import models
from pausedefi_api import app
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields

ma = Marshmallow(app)


class ChallengeSchema(ma.SQLAlchemyAutoSchema):
    challengers = ma.Nested(lambda: UserSchema(exclude=['challenges']), many=True)
    rooms = ma.Nested(lambda: RoomSchema(exclude=['challenges', 'bio']), many=True)
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)

    class Meta:
        model = models.Challenge


class UserSchema(ma.SQLAlchemyAutoSchema):
    password = fields.Str(load_only=True)
    challenges = ma.Nested(lambda: ChallengeSchema(exclude=['challengers']), many=True)
    rooms = ma.Nested(lambda: RoomSchema(exclude=['challenges']), many=True)
    rooms_created = ma.Nested(lambda: RoomSchema(exclude=['challenges']), many=True)

    class Meta:
        model = models.User


class RoomSchema(ma.SQLAlchemyAutoSchema):
    access = fields.Str(load_only=True)
    challenges = ma.Nested(lambda: ChallengeSchema(), many=True)
    users = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)
    creator = ma.Nested(lambda: UserSchema(exclude=['challenges', 'rooms', 'rooms_created']), many=True)

    class Meta:
        model = models.Room