from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql


# APP DEFINITION
app = Flask(__name__)
app.config['SECRET_KEY'] = '9BFhxkza1GySNi5WuPnRzZtTJw_hBEIz'


# MYSQL CONFIG
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = '3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'IIMmysql=444719'
app.config['MYSQL_DB'] = 'pausedefi_db'


# DB INIT
pymysql.install_as_MySQLdb()


# SQLALCHEMY CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + app.config['MYSQL_USER'] + ':' + app.config['MYSQL_PASSWORD'] + '@' + app.config['MYSQL_HOST'] + ':' + app.config['MYSQL_PORT'] + '/' + app.config['MYSQL_DB']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from pausedefi_api import routes
