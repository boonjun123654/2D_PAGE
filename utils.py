import random

def generate_2d_result():
    """
    随机生成 6 个号码（不重复），格式化为 2 位数
    返回格式：
    {
        "specials": ['13', '27', '35', '44', '66', '87']
    }
    """
    numbers = random.sample(range(1, 100), 6)
    numbers.sort()
    return {
        "specials": [f"{n:02}" for n in numbers]
    }
