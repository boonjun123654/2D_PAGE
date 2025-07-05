from config import Config
from models import db
from scheduler import manual_trigger
from flask import Flask, request, render_template, jsonify
from models import db, Result2D

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route('/')
    def index():
        return "2D Results App OK"

    @app.route('/test-draw')
    def test_draw():
        draw_no = request.args.get('draw_no')
        if not draw_no:
            return "❌ 请使用 ?draw_no=20250705-09 指定期号", 400
        manual_trigger(draw_no)
        return f"✅ 已手动执行完整开奖流程：{draw_no}"

    @app.route('/latest')
    def latest():
        latest_result = Result2D.query.order_by(Result2D.id.desc()).first()

        if not latest_result:
        return "⚠️ 暂无开奖结果"
    
        specials = []
        for i in range(1, 7):
            specials.append(getattr(latest_result, f'special_{i}'))

        return render_template('latest.html', result=latest_result, specials=specials)


    # ✅ 新增 AJAX API：点击按钮时调用此接口
    @app.route('/latest/step', methods=['POST'])
    def step_latest():
        latest_result = Result2D.query.order_by(Result2D.id.desc()).first()
        if not latest_result:
            return jsonify({"ok": False, "msg": "未找到最新期"}), 400
        manual_trigger(latest_result.draw_no)
        return jsonify({"ok": True})

    return app

# ✅ 这个是 gunicorn 要找的变量
app = create_app()
