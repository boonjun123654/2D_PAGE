from config import Config
from models import db
from scheduler import start_scheduler
from flask import Flask, request

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    start_scheduler(app)

    @app.route('/')
    def index():
        return "2D Results App OK"

    @app.route('/test-draw')
    def test_draw():
        draw_no = request.args.get('draw_no')
        if not draw_no:
            return "❌ 请使用 ?draw_no=20250705-09 指定期号", 400
        manual_trigger(draw_no)
        return f"✅ 已手动执行开奖步骤：{draw_no}"

    return app

# ✅ 这个是 gunicorn 要找的变量
app = create_app()
