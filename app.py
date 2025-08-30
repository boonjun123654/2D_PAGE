from flask import Flask, render_template, session, jsonify
import random
from datetime import datetime, timedelta
from pytz import timezone
from models import db, DrawResult  # 你的2D模型
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

MY_TZ = timezone("Asia/Kuala_Lumpur")
scheduler = BackgroundScheduler(timezone=str(MY_TZ))

app = Flask(__name__)
app.secret_key = 'secret123'  # 用于 session

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
    now = datetime.now(MY_TZ)
    if 9 <= now.hour <= 23 and now.minute == 40:
        slot = now.replace(minute=50, second=0, microsecond=0)
        code = slot.strftime("%Y%m%d/%H%M")
        deleted = DrawResult.query.filter_by(code=code).delete()
        db.session.commit()
        print(f"[clear] {code} deleted={deleted}")

# 每小时 :40 清空
scheduler.add_job(clear_upcoming_slot_draws, CronTrigger(hour='9-23', minute='40'))

# 你原来的 :50 生成任务保留（示例）：
# scheduler.add_job(generate_numbers_for_time, CronTrigger(minute='50'))

scheduler.start()

# ==== 前端读取接口：/draw?market=M ====
@app.route('/draw')
def api_draw():
    market = request.args.get('market', 'M')
    code, slot_dt = _current_slot_code()

    r = DrawResult.query.filter_by(code=code, market=market)\
                        .order_by(DrawResult.id.desc()).first()

    if not r:
        # 若还没生成到当期，返回空
        return jsonify({"code": code, "market": market, "head": None, "special": []})

    # specials 建议存 "07,42,88" 这种；这里只取前3个
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

def generate_draw_code():
    today = datetime.now().strftime("%Y%m%d")
    if 'draw_count' not in session:
        session['draw_count'] = 1
    else:
        session['draw_count'] += 1
    return f"{today}{session['draw_count']:02d}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/draw')
def draw():
    draw_code = generate_draw_code()
    all_numbers = list(range(1, 100))
    selected = random.sample(all_numbers, 6)
    special = [f"{n:02d}" for n in selected]  # 全部为特别奖，头奖留空
    return jsonify({
        "code": draw_code,
        "special": special
    })

if __name__ == '__main__':
    app.run(debug=True)
