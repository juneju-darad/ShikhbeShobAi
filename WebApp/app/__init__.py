import os
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_login import LoginManager
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = '11f0c9648013c9a24e29a1e3f8579585'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt  = Bcrypt(app)
json = FlaskJSON(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app import routes