from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DrawResult(db.Model):
    __tablename__ = 'draw_results'
    id = db.Column(db.Integer, primary_key=True)
    draw_no = db.Column(db.String(20), unique=True, nullable=False)  # 格式: 20250706-09
    draw_time = db.Column(db.DateTime, nullable=False)
    special_numbers = db.Column(db.String(20), nullable=False)  # "10,24,55,46,99,87"
    head_number = db.Column(db.String(2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
