from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
from models import User


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'i dont know'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasker.db'
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = '6379'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    


    
    cache = Cache(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)

    @login_manager.user_loader

    def load_user(userid):
        return User.query.get(int(userid))
    from routes import init_routes
    init_routes(app, db, bcrypt,cache)

    migrate= Migrate(app,db)
    

    return app



