from flask import request, render_template
from pausedefi_api import app
from pausedefi_api.models import *


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['POST'])
def register():
    content = request.json
    email = content['email']
    password = content['password']

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return 'User registered.'
