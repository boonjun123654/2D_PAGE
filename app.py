from flask import Flask, render_template, redirect, url_for, session
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'  # 用于 session

# 局号计数器（简单自增，真实应改为数据库编号）
def generate_draw_code():
    today = datetime.now().strftime("%Y%m%d")
    if 'draw_count' not in session:
        session['draw_count'] = 1
    else:
        session['draw_count'] += 1
    return f"{today}{session['draw_count']:02d}"

def generate_numbers():
    all_numbers = list(range(1, 100))
    selected = random.sample(all_numbers, 6)
    head = selected[0]
    special = selected[1:]
    return head, special

@app.route('/')
def index():
    draws = session.get('draws', [])
    return render_template('index.html', draws=draws)

@app.route('/draw')
def draw():
    draw_code = generate_draw_code()
    head, special = generate_numbers()

    # 新局插入到列表最前方（最新在上）
    new_draw = {
        'code': draw_code,
        'head': f"{head:02d}",
        'special': [f"{num:02d}" for num in special]
    }

    draws = session.get('draws', [])
    draws.insert(0, new_draw)
    session['draws'] = draws

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
