from flask import request, render_template, jsonify
from pausedefi_api.models import *
from pausedefi_api.schemas import *
from werkzeug.security import generate_password_hash
import jwt
from functools import wraps


# SECURITY
def auth_token_required(func):
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        bearer = request.headers.get('Authorization')
        token = bearer.split()[1]
        if not token:
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
    return jsonify({'token': token}), 200


# ROUTES
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/api/user/me')
@auth_token_required
def get_me():

    return UserSchema(many=True).jsonify(User.query.all())


@app.route('/users')
@auth_token_required
def get_all_users():
    return UserSchema(many=True).jsonify(User.query.all())


@app.route('/challenges')
@auth_token_required
def get_all_challenges():
    return ChallengeSchema(many=True).jsonify(Challenge.query.all())


@app.route('/rooms')
@auth_token_required
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


@app.route('/login', methods=['POST'])
def login():
    content = request.json
    email = content['email']
    password = content['password']

    user = User.query.filter(User.email == email).first()
    if user.check_password(password):
        return auth_token_generate(email)
    return jsonify({'error': 'TOCARD'}), 401
