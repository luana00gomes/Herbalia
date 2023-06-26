from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from . import db

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    
    verification_token = db.Column(db.String(100), unique=True)  # Adicione o campo para armazenar o token de verificação
    reset_token = db.Column(db.String(100), unique=True)
    is_verified = db.Column(db.Boolean, default=False)  # Adicione um campo para rastrear se o e-mail foi verificado ou não

    def update_password(self, new_password):
        self.password = generate_password_hash(new_password)
        db.session.commit()

class Plants(UserMixin, db.Model):
    __tablename__ = 'plants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    name = db.Column(db.String(100))
    time_light_on = db.Column(db.Integer)
    light_indice = db.Column(db.Integer)
    humidity_indice = db.Column(db.Integer)

    def __init__(self, user_id, name, time_light_on, light_indice, humidity_indice):
        self.user_id = int(user_id)
        self.name = name
        self.time_light_on = int(time_light_on)
        self.light_indice = int(light_indice)
        self.humidity_indice = int(humidity_indice)


class Text(db.Model):
    __tablename__ = 'text'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    content = db.Column(db.String)