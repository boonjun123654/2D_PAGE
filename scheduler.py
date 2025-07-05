from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import db, Result2D
from utils import generate_2d_result

def generate_draw():
    now = datetime.now()
    draw_no = now.strftime("%Y%m%d-%H")
    draw_date = now.date()

    # 已存在该期则跳过
    if Result2D.query.filter_by(draw_no=draw_no).first():
        print(f"[{draw_no}] 已存在，跳过")
        return

    result = generate_2d_result()

    new_result = Result2D(
        draw_date=draw_date,
        draw_no=draw_no,
        prize_1st=result["prize_1st"],
        special_1=result["specials"][0],
        special_2=result["specials"][1],
        special_3=result["specials"][2],
        special_4=result["specials"][3],
        special_5=result["specials"][4],
        is_even=result["is_even"],
        is_big=result["is_big"]
    )
    db.session.add(new_result)
    db.session.commit()
    print(f"✅ [{draw_no}] 开奖完成！")

def start_scheduler(app):
    scheduler = BackgroundScheduler(timezone="Asia/Kuala_Lumpur")
    with app.app_context():
        # 每小时第 50 分钟执行（09:50~23:50）
        scheduler.add_job(generate_draw, 'cron', hour='9-23', minute=50)
        scheduler.start()
