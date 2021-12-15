from flask import request, render_template, jsonify
from pausedefi_api.models import *
from pausedefi_api.schemas import *
from werkzeug.security import generate_password_hash
import jwt
from functools import wraps
from sqlalchemy import or_
#import pymysql

#pymysql.install_as_MySQLdb()


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


def auth_token_generate(email):
    token = jwt.encode({
        'email': email  # ,
        # 'expiration': str(datetime.utcnow() + timedelta(seconds=60))
    }, app.config['SECRET_KEY'])
    return jsonify({'access_token': token}), 200


def decode_auth_token(auth_header):
    token = auth_header.split()[1]
    email = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])['email']
    return email


# ROUTES
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# ROOM
@app.route('/api/room', methods=['POST'])
@auth_token_required
def create_room():
    room = Room(
        name=request.json['name'],
        bio=request.json['bio']
    )
    room.creator_id = request.json['creator_id']
    db.session.add(room)
    failed = False
    try:
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        failed = True
    if not failed:
        return jsonify({'access_code': room.access})
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/room/access', methods=['POST'])
@auth_token_required
def access_room():
    room = Room.query.filter(Room.access == request.json["access_code"]).first()
    user = User.query.filter(User.id == request.json["user_id"]).first()
    room.users.append(user)
    db.session.add(room)
    failed = False
    try:
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        failed = True
    if not failed:
        return jsonify(), 200
    else:
        return jsonify({"error": "Not able to save in db"}), 500


@app.route('/api/room/<int:id>')
@auth_token_required
def get_room_by_id(id):
    return RoomSchema().jsonify(Room.query.filter(Room.id == id).first())


@app.route('/api/users/me/rooms')
@auth_token_required
def get_my_rooms():
    email = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.email == email).first()
    return RoomSchema(many=True).jsonify(Room.query.filter(or_(Room.users.any(id=user.id), user.id == Room.creator_id)))


@app.route('/api/users/me')
@auth_token_required
def get_me():
    email = decode_auth_token(request.headers.get('Authorization'))
    user = User.query.filter(User.email == email).first()
    return UserSchema().jsonify(user)


@app.route('/users')
# @auth_token_required
def get_all_users():
    return UserSchema(many=True).jsonify(User.query.all())


@app.route('/challenges')
# @auth_token_required
def get_all_challenges():
    return ChallengeSchema(many=True).jsonify(Challenge.query.all())


@app.route('/rooms')
# @auth_token_required
def get_all_rooms():
    return RoomSchema(many=True).jsonify(Room.query.all())


@app.route('/register', methods=['POST'])
def register():
    content = request.json
    email = content['email']
    password = generate_password_hash(content['password'])

    user = User(email=email, password=password)
    db.session.add(user)
    try:
        db.session.commit()
        failed = False
    except:
        failed = True
    if not failed:
        return auth_token_generate(email)
    return jsonify({'error': 'TOCARD'}), 401


@app.route('/auth/login', methods=['POST'])
def login():
    content = request.form
    try:
        email = content['email']
        password = content['password']

        user = User.query.filter(User.email == email).first()
        if user.check_password(password):
            return auth_token_generate(email)
        return jsonify({'error': 'TOCARD'}), 401
    except:
        return jsonify({'error': 'Aucune donnée'}), 500
