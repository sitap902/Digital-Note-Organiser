from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text
from os import path


db = SQLAlchemy()
DB_NAME = "database.db"


def ensure_note_columns():
    required_columns = {
        'title': "ALTER TABLE note ADD COLUMN title VARCHAR(200) DEFAULT 'Untitled note'",
        'notebook': "ALTER TABLE note ADD COLUMN notebook VARCHAR(100) DEFAULT 'My Notes'",
        'tags': "ALTER TABLE note ADD COLUMN tags VARCHAR(200) DEFAULT ''",
        'pinned': "ALTER TABLE note ADD COLUMN pinned BOOLEAN DEFAULT 0",
        'file': "ALTER TABLE note ADD COLUMN file VARCHAR(300)",
    }

    existing = {
        row[1]
        for row in db.session.execute(text("PRAGMA table_info(note)")).fetchall()
    }

    for column_name, statement in required_columns.items():
        if column_name not in existing:
            db.session.execute(text(statement))

    db.session.commit()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = path.join(app.root_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

    with app.app_context():
        db.create_all()
        ensure_note_columns()
        if not path.exists(app.config['UPLOAD_FOLDER']):
            from os import makedirs
            makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    login_manager = LoginManager()
    login_manager.login_view = '/login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect('/login')

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
