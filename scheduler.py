from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import db, Result2D
from utils import generate_2d_result
import random

# 状态记录（用于追踪开奖步骤 0~6）
draw_state = {}

def process_step(draw_no):
    now = datetime.now()
    draw_date = now.date()

    # 当前状态（0~6），默认从 0 开始
    step = draw_state.get(draw_no, 0)

    if step == 0:
        # 初始开奖：生成 6 个特别奖号码
        result = generate_2d_result()
        numbers = result["specials"]

        existing = Result2D.query.filter_by(draw_no=draw_no).first()
        if existing:
            return  # 已存在跳过

        new_result = Result2D(
            draw_date=draw_date,
            draw_no=draw_no,
            special_1=numbers[0],
            special_2=numbers[1],
            special_3=numbers[2],
            special_4=numbers[3],
            special_5=numbers[4],
            special_6=numbers[5],
        )
        db.session.add(new_result)
        db.session.commit()
        print(f"Step 0: [{draw_no}] 已生成特别奖号码")
        draw_state[draw_no] = 1

    elif 1 <= step < 6:
        # 只是计数阶段，无实际操作
        print(f"Step {step}: 等待中 [{draw_no}]")
        draw_state[draw_no] = step + 1

    elif step == 6:
        # 最终阶段：从 6 个特别奖中抽出一个做头奖
        result = Result2D.query.filter_by(draw_no=draw_no).first()
        if not result:
            return

        all_numbers = [
            result.special_1, result.special_2, result.special_3,
            result.special_4, result.special_5, result.special_6
        ]

        prize_1st = random.choice(all_numbers)
        remaining = [n for n in all_numbers if n != prize_1st]

        # 重新排序剩下的特别奖
        result.prize_1st = prize_1st
        result.special_1 = remaining[0]
        result.special_2 = remaining[1]
        result.special_3 = remaining[2]
        result.special_4 = remaining[3]
        result.special_5 = remaining[4]
        result.special_6 = None  # 清空

        # 头奖单双/大小判断
        result.is_even = int(prize_1st) % 2 == 0
        result.is_big = int(prize_1st) >= 51

        db.session.commit()
        print(f"✅ Step 6: [{draw_no}] 已完成最终开奖，头奖为 {prize_1st}")
        draw_state.pop(draw_no)  # 删除状态

# 手动测试入口：一次执行完整开奖流程（step 0 ~ 6）
def manual_trigger(draw_no):
    for _ in range(7):
        process_step(draw_no)

def start_scheduler(app):
    scheduler = BackgroundScheduler(timezone="Asia/Kuala_Lumpur")

    def step_handler():
        now = datetime.now()
        hour = now.strftime('%H')
        minute = now.minute
        if hour >= '09' and hour <= '23' and minute >= 50 and minute <= 54:
            draw_no = now.strftime('%Y%m%d-%H')
            with app.app_context():
                process_step(draw_no)

    scheduler.add_job(step_handler, 'interval', seconds=30)
    scheduler.start()
