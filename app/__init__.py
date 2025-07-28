from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    try:
        # Загрузка конфигурации
        app.config.from_object('config.Config')
        
        # Инициализация расширений
        db.init_app(app)
        login_manager.init_app(app)
        bcrypt.init_app(app)
        login_manager.login_view = 'views.login'
        
        from .models import User
        
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception as e:
                return None
        
        from .app import views
        app.register_blueprint(views)
        
        with app.app_context():
            db.create_all()
            
    except Exception as e:
        print('Notice me')
    
    return app