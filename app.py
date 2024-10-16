from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
from models import User


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'i dont know'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasker.db'

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader

    def load_user(userid):
        return User.query.get(int(userid))
    from routes import init_routes
    init_routes(app, db, bcrypt)

    migrate= Migrate(app,db)

    return app



