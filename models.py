from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Result2D(db.Model):
    __tablename__ = 'results_2d_page'

    id = db.Column(db.Integer, primary_key=True)
    draw_date = db.Column(db.Date, nullable=False)
    draw_no = db.Column(db.String(20), unique=True, nullable=False)  # e.g. 20250703-09
    prize_1st = db.Column(db.String(2), nullable=False)
    special_1 = db.Column(db.String(2), nullable=False)
    special_2 = db.Column(db.String(2), nullable=False)
    special_3 = db.Column(db.String(2), nullable=False)
    special_4 = db.Column(db.String(2), nullable=False)
    special_5 = db.Column(db.String(2), nullable=False)
    is_even = db.Column(db.Boolean)
    is_big = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
