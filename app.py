from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from datetime import datetime
import random

app = Flask(__name__)

# ====== 配置 ======
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_4m_user:xiOe63X4iaczwTAcNfUYwS8oWrDExkHX@dpg-d11rb03uibrs73eh87vg-a/db_4m'  # 可换成 PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'Asia/Kuala_Lumpur'
app.secret_key = 'secret123'

# ====== 初始化 ======
db = SQLAlchemy(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# ====== 模型 ======
class DrawResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    draw_no = db.Column(db.String(20), unique=True, nullable=False)  # 20250706-09
    draw_time = db.Column(db.DateTime, nullable=False)
    special_numbers = db.Column(db.String(20), nullable=False)  # "10,24,55,46,99,87"
    head_number = db.Column(db.String(2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def get_connection():
    return psycopg2.connect(
        dbname='你的数据库名',
        user='你的用户名',
        password='你的密码',
        host='你的主机（通常是 localhost 或 render 的连接地址）',
        port='5432'
    )

def get_current_draw_no():
    now = datetime.now()
    hour = now.hour
    if hour < 9 or hour > 23:
        return None  # 非开奖时间

    draw_no = now.strftime('%Y%m%d') + '-' + f"{hour:02d}"
    return draw_no


# ====== 自动开奖函数 ======
def generate_draw(draw_hour):
    today_str = datetime.now().strftime("%Y%m%d")
    draw_no = f"{today_str}-{draw_hour:02d}"

    if DrawResult.query.filter_by(draw_no=draw_no).first():
        return  # 已开奖

    nums = random.sample(range(0, 100), 6)
    formatted = [f"{n:02d}" for n in nums]
    head = random.choice(formatted)

    result = DrawResult(
        draw_no=draw_no,
        draw_time=datetime.now().replace(hour=draw_hour, minute=50, second=0, microsecond=0),
        special_numbers=','.join(formatted),
        head_number=head
    )
    db.session.add(result)
    db.session.commit()

# ====== 添加任务 ======
for hour in range(9, 24):
    scheduler.add_job(
        id=f'draw_{hour}',
        func=lambda h=hour: generate_draw(h),
        trigger='cron', hour=hour, minute=50,
        replace_existing=True
    )

# ====== 网页展示 ======
@app.route('/')
def index():
    today = datetime.now().strftime("%Y%m%d")
    results = DrawResult.query.filter(DrawResult.draw_no.startswith(today)).order_by(DrawResult.draw_no).all()
    return render_template('index.html', results=results)

def index():
    ...
    markets = [
        {"code": "M", "name": "Magnum", "color": "#ffff00", "logo": "magnum.png"},
        {"code": "P", "name": "Damacai", "color": "#0000ff", "logo": "damacai.png"},
        {"code": "T", "name": "SportsToto", "color": "#cc0000", "logo": "toto.png"},
        {"code": "S", "name": "Singapore", "color": "#4c8ed1", "logo": "singapore.png"},
        {"code": "H", "name": "Grand Dragon", "color": "#ff0000", "logo": "grand_dragon.png"},
        {"code": "E", "name": "9 Lotto", "color": "#ffa500", "logo": "9lotto.png"},
        {"code": "B", "name": "Sabah", "color": "#e51d20", "logo": "sabah.png"},
        {"code": "K", "name": "Sandakan", "color": "#008835", "logo": "sandakan.png"},
        {"code": "W", "name": "Sarawak", "color": "#00540e", "logo": "sarawak.png"},
    ]
    return render_template('index.html', results=results, markets=markets)


# ====== API 结果读取 ======
@app.route('/draw')
def draw():
    today = datetime.now().strftime("%Y%m%d")
    results = DrawResult.query.filter(DrawResult.draw_no.startswith(today)).order_by(DrawResult.draw_no).all()
    latest = results[-1] if results else None
    if latest:
        return jsonify({
            "code": latest.draw_no,
            "special": latest.special_numbers.split(','),
            "head": latest.head_number
        })
    return jsonify({"code": "N/A", "special": [], "head": "--"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
