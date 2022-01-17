from flask import request, render_template, jsonify
from pausedefi_api.models import *
from pausedefi_api.schemas import *
import jwt
from functools import wraps
from sqlalchemy import or_, and_, asc
import pymysql

# pymysql.install_as_MySQLdb()


# SECURITY
def auth_token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        bearer = request.headers.get('Authorization')
        if bearer is not None:
            token = bearer.split()[1]
        else:
            token = None
        if token is None:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'error': 'Invalid token'}), 403
        return func(*args, **kwargs)

    return decorated


def auth_token_generate(user_id):
    token = jwt.encode({
        'user_id': user_id  # ,
        # 'expiration': str(datetime.utcnow() + timedelta(seconds=60))
    }, app.config['SECRET_KEY'])
    return jsonify({'access_token': token}), 200


def decode_auth_token(auth_header):
    token = auth_header.split()[1]
    user_id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])['user_id']
    return user_id


def save_in_db():
    try:
        db.session.commit()
        return False
    except Exception as e:
        print(e)
        db.session.rollback()
        db.session.flush()
        return True


# ROUTES
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# ROOM
@app.route('/api/room/create', methods=['POST'])
@auth_token_required
def create_room():
    room = RoomSchema().load(request.get_json(), partial=True)
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    room.creator_id = user.id
    room.creator = user
    room.add_users([user])
    db.session.add(room)
    failed = save_in_db()
    if not failed:
        return jsonify({'access_code': room.access, 'id': room.id})
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/room/access', methods=['PUT'])
@auth_token_required
def access_room():
    room = Room.query.filter(Room.access == request.json["access_code"]).first()
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    room.add_users([user])
    db.session.add(room)
    failed = save_in_db()
    if not failed:
        return RoomSchema().jsonify(room), 200
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/room/<int:id>')
@auth_token_required
def get_room_by_id(id):
    return RoomSchema().jsonify(Room.query.filter(Room.id == id).first())


@app.route('/api/room/<int:id>/users')
@auth_token_required
def get_users_in_room(id):
    user_id = decode_auth_token(request.headers.get('Authorization'))
    order_by = request.args.get('order_by', type=str)
    if order_by is not None:
        return UserSchema(many=True, context={'room_id': id}).jsonify(User.query.filter(or_(User.rooms.any(id=id), User.rooms.any(creator_id=User.id))).join(User.room_users).order_by(RoomUsers.points).all())
    else:
        return UserSchema(many=True, context={'room_id': id}).jsonify(User.query.filter(or_(User.rooms.any(id=id), User.rooms_created.any(id=id))).filter(User.id != user_id).all())


@app.route('/api/room/<int:room_id>/challenges/<int:challenge_id>/challengers', methods=['POST'])
@auth_token_required
def add_challengers(room_id, challenge_id):
    user_id = decode_auth_token(request.headers.get('Authorization'))
    challengers = User.query.filter(User.id.in_(request.json["challengers"])).all()
    room = Room.query.filter(Room.id == room_id).first()
    challenge = (i for i, e in enumerate(room.challenges) if e.id == challenge_id)
    challenge_index = next(challenge)
    room.challenges[challenge_index].creator_id = user_id
    room.challenges[challenge_index].add_users(challengers)
    db.session.add(room)
    failed = save_in_db()
    if not failed:
        return '', 204
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/room/<int:id>/challenge', methods=['POST'])
@auth_token_required
def create_challenge(id):
    room = Room.query.filter(Room.id == id).first()
    challenge = ChallengeSchema().load(request.get_json(), partial=True)
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    mails = []
    for challenger in challenge.challengers:
        mails.append(challenger.email)
    challengers = User.query.filter(User.email.in_(mails)).all()
    challenge.creator_id = user.id
    challenge.creator = user
    challenge.room = room
    challenge.room_id = id
    challenge.date_posted = datetime.now()
    challenge.challengers = challengers
    challenge.add_users(challengers)
    db.session.add(challenge)
    failed = save_in_db()
    if not failed:
        return '', 204
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/room/<int:id>/challenges/me')
@auth_token_required
def get_my_challenges(id):
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    return ChallengeSchema(many=True, context={'user_id': user_id}).jsonify(Challenge.query.filter(and_(Challenge.challengers.any(id=user.id), Challenge.room_id == id)))


@app.route('/api/room/<int:id>/challenges/idea')
@auth_token_required
def get_idea_challenge(id):
    return ChallengeSchema(many=True).jsonify(Challenge.query.filter(~Challenge.challengers.any()))


@app.route('/api/room/<int:id>/challenges/me/send')
@auth_token_required
def get_my_send_challenges(id):
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    return ChallengeSchema(many=True).jsonify(Challenge.query.filter(and_(Challenge.creator_id == user.id, Challenge.room_id == id)).filter(Challenge.challengers != None))


@app.route('/api/users/me')
@auth_token_required
def get_me():
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    return UserSchema().jsonify(user)


@app.route('/api/users/me/challenges/<int:challenge_id>', methods=['PATCH'])
@auth_token_required
def update_state(challenge_id):
    room_id = request.json['room_id']
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    for i in range(0, len(user.challenges)):
        if user.challenges[i].id == challenge_id:
            index = i
    user.challenges[index].update_state(state=ChallengeState(request.json['state']), user_id=user_id)
    room = Room.query.filter(Room.id == room_id).first()
    room.update_point(point=user.challenges[index].points, user_id=user_id)
    db.session.add(user)
    failed = save_in_db()
    if not failed:
        return ChallengeUsersSchema().jsonify(ChallengeUsers.query.filter(ChallengeUsers.challenge_id == challenge_id).first()), 200
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/users/me/rooms')
@auth_token_required
def get_my_rooms():
    user_id = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.id == user_id).first()
    return RoomSchema(many=True, exclude=['challenges', 'users']).jsonify(Room.query.filter(or_(Room.users.any(id=user.id), user.id == Room.creator_id)))


@app.route('/auth/register', methods=['POST'])
def register():
    content = request.json
    user = User(**content)
    db.session.add(user)
    failed = save_in_db()
    if not failed:
        return auth_token_generate(user.id)
    return jsonify({'error': 'TOCARD'}), 401


@app.route('/auth/login', methods=['POST'])
def login():
    content = request.json
    try:
        email = content['email']
        password = content['password']

        user = User.query.filter(User.email == email).first()
        if user.check_password(password):
            return auth_token_generate(user.id)
        return jsonify({'error': 'TOCARD'}), 401
    except:
        return jsonify({'error': 'Aucune donnée'}), 500


@app.route('/users')
# @auth_token_required
def get_all_users():
    return UserSchema(many=True).jsonify(User.query.all())


@app.route('/challenges')
# @auth_token_required
def get_all_challenges():
    # specify this argument next to 'many' : context={'user_id':2}, give you access to state field in challenge for a given user_id
    return ChallengeSchema(many=True).jsonify(Challenge.query.all())


@app.route('/rooms')
# @auth_token_required
def get_all_rooms():
    return RoomSchema(many=True).jsonify(Room.query.all())


@app.route('/test-deploy')
def test_deploy():
    return "C'est déployé"