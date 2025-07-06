from flask import Flask, render_template, session, jsonify
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'  # 用于 session

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
