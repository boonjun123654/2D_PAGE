from flask import Flask
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route('/')
    def index():
        return "2D Results App OK"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
