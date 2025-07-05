from flask import Flask
from config import Config
from models import db
from scheduler import start_scheduler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    start_scheduler(app)

    @app.route('/')
    def index():
        return "2D Results App OK"

    return app

# ✅ 这个是 gunicorn 要找的变量
app = create_app()
