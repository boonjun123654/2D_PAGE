import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

MY_TZ = timezone("Asia/Kuala_Lumpur")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")

# === DB ===
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

# === Scheduler ===
scheduler = BackgroundScheduler(timezone=str(MY_TZ))

def _current_slot_code(now=None):
    """返回最近一次 :50 的期号 例如 20250830/0950，并返回对应 datetime"""
    now = now or datetime.now(MY_TZ)
    hour, minute = now.hour, now.minute
    if minute < 50:
        hour -= 1
    base = now.replace(hour=hour, minute=50, second=0, microsecond=0)
    return base.strftime("%Y%m%d/%H%M"), base

def clear_upcoming_slot_draws():
    """09:40/10:40/.../23:40 清空即将开奖的本小时 :50 记录"""
    with app.app_context():
        now = datetime.now(MY_TZ)
        if 9 <= now.hour <= 23 and now.minute == 40:
            slot = now.replace(minute=50, second=0, microsecond=0)
            code = slot.strftime("%Y%m%d/%H%M")
            db.session.execute(text("DELETE FROM draw_results WHERE code = :code"), {"code": code})
            db.session.commit()
            print(f"[clear] {code} deleted")

# 注册 :40 清空任务
scheduler.add_job(clear_upcoming_slot_draws, CronTrigger(hour='9-23', minute='40'))

# ⚠️ 直接在导入时启动（请在 Render 设置 WEB_CONCURRENCY=1，确保单 worker）
if not scheduler.running:
    scheduler.start()
    print("[scheduler] started")

# === API: 前端读取接口 /draw?market=M ===
@app.route('/draw')
def api_draw():
    market = request.args.get('market', 'M')
    code, _ = _current_slot_code()

    row = db.session.execute(
        text("""
            SELECT id, code, market, head, specials, parity_type, size_type
            FROM draw_results
            WHERE code = :code AND market = :market
            ORDER BY id DESC
            LIMIT 1
        """),
        {"code": code, "market": market}
    ).mappings().first()

    if not row:
        return jsonify({"code": code, "market": market, "head": None, "special": []})

    specials = []
    if row.get("specials"):
        specials = [s.strip().zfill(2) for s in row["specials"].split(",") if s.strip()][:3]

    resp = {
        "code": row["code"],
        "market": row["market"],
        "head": (row["head"].zfill(2) if row.get("head") else None),
        "special": specials,
    }
    if row.get("parity_type"):
        resp["parity"] = row["parity_type"]
    if row.get("size_type"):
        resp["size"] = row["size_type"]
    return jsonify(resp)

# === Page ===
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
