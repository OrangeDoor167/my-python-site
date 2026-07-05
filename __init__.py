import os

from flask import Flask, session


class AnonymousUser:
    is_authenticated = False
    email = None
    is_owner = False


class AuthenticatedUser:
    def __init__(self, email, is_owner=False):
        self.email = email
        self.is_authenticated = True
        self.is_owner = is_owner


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "I like pizza yay"
    app.config['OWNER_EMAIL'] = 'ld131@bcps.org'
    app.config['OWNER_PASSWORD'] = 'about217'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.context_processor
    def inject_user():
        user_email = session.get('user')
        if user_email:
            is_owner = user_email == app.config['OWNER_EMAIL']
            return {'user': AuthenticatedUser(user_email, is_owner)}
        return {'user': AnonymousUser()}

    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    return app