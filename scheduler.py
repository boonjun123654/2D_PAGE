from datetime import datetime
from models import db, Result2D  # 请确认你的模型文件名和类名
from utils import generate_2d_result
import random
import time

def manual_trigger(draw_no):
    now = datetime.now()
    draw_date = now.date()

    # 第一步：生成 6 个特别奖号码
    result = generate_2d_result()
    numbers = result["specials"]

    existing = Result2D.query.filter_by(draw_no=draw_no).first()
    if existing:
        print(f"❌ [{draw_no}] 已存在，跳过生成")
        return

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
    print(f"✅ [{draw_no}] 已生成特别奖号码")

    # 等待5秒后继续执行头奖
    time.sleep(5)

    # 第二步：抽出头奖号码
    prize_1st = random.choice(numbers)
    remaining = [n for n in numbers if n != prize_1st]

    # 更新数据库记录
    new_result.prize_1st = prize_1st
    new_result.special_1 = remaining[0]
    new_result.special_2 = remaining[1]
    new_result.special_3 = remaining[2]
    new_result.special_4 = remaining[3]
    new_result.special_5 = remaining[4]
    new_result.special_6 = None
    new_result.is_even = int(prize_1st) % 2 == 0
    new_result.is_big = int(prize_1st) >= 51

    db.session.commit()
    print(f"🎯 [{draw_no}] 已完成开奖，头奖为 {prize_1st}")
