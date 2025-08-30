import os
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
from pytz import timezone
from models import db, DrawResult
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

MY_TZ = timezone("Asia/Kuala_Lumpur")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")  # 建议用环境变量

# 若未在别处配置，请确保已设置 DB 并初始化
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

scheduler = BackgroundScheduler(timezone=str(MY_TZ))

# ==== 工具：计算“最近一次 :50”期号 ====
def _current_slot_code(now=None):
    """返回最近一次 :50 的期号，例如 20250830/0950，并返回对应的 datetime"""
    now = now or datetime.now(MY_TZ)
    hour, minute = now.hour, now.minute
    if minute < 50:
        hour -= 1
    base = now.replace(hour=hour, minute=50, second=0, microsecond=0)
    return base.strftime("%Y%m%d/%H%M"), base

# ==== 09:40/10:40/…/23:40 清空即将开奖的时段 ====
def clear_upcoming_slot_draws():
    with app.app_context():
        now = datetime.now(MY_TZ)
        if 9 <= now.hour <= 23 and now.minute == 40:
            slot = now.replace(minute=50, second=0, microsecond=0)
            code = slot.strftime("%Y%m%d/%H%M")
            deleted = DrawResult.query.filter_by(code=code).delete()
            db.session.commit()
            print(f"[clear] {code} deleted={deleted}")

# 每小时 :40 清空
scheduler.add_job(clear_upcoming_slot_draws, CronTrigger(hour='9-23', minute='40'))

# （保留你的 :50 生成任务）
# scheduler.add_job(generate_numbers_for_time, CronTrigger(minute='50'))

# 仅启动一次调度器
_scheduler_started = False
@app.before_first_request
def _start_scheduler_once():
    global _scheduler_started
    if not _scheduler_started:
        scheduler.start()
        _scheduler_started = True

# ==== 前端读取接口：/draw?market=M ====
@app.route('/draw')
def api_draw():
    market = request.args.get('market', 'M')
    code, _ = _current_slot_code()

    r = DrawResult.query.filter_by(code=code, market=market) \
                        .order_by(DrawResult.id.desc()).first()

    if not r:
        # 若当期尚未生成，返回空
        return jsonify({"code": code, "market": market, "head": None, "special": []})

    specials = []
    if getattr(r, "specials", None):
        specials = [s.strip().zfill(2) for s in r.specials.split(',') if s.strip()][:3]

    resp = {
        "code": r.code,
        "market": r.market,
        "head": (r.head.zfill(2) if r.head else None),
        "special": specials,
    }
    if hasattr(r, "parity_type"): resp["parity"] = r.parity_type  # 单/双（可选）
    if hasattr(r, "size_type"):   resp["size"]   = r.size_type    # 大/小（可选）
    return jsonify(resp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 本地开发时从这里启动
    with app.app_context():
        if not _scheduler_started:
            scheduler.start()
            _scheduler_started = True
    app.run(debug=True)
