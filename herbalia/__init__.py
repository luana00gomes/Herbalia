from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


# init Mail
from flask_mail import Mail
mail = Mail()


def create_app():
    #App config
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    app.config['MAIL_USER'] = os.environ['MAIL_USER']
    db.init_app(app)   
    mail.init_app(app)
    #connects to db

    #Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)    

    from .models import Users
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for content parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    @app.context_processor
    def inject_user_plants():
        from .models import Plants
        user_plants = []
        
        if current_user.is_authenticated:
            user_plants = Plants.query.filter_by(user_id=current_user.get_id()).all()
            print("Got: ", user_plants)

        user_plants_dict = {plant.id: plant for plant in user_plants}
        print("Returning: ")
        print({'user_plants': user_plants_dict})
        return {'user_plants': user_plants_dict}


    return app