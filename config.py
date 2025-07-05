import os

class Config:
    # Render 部署时建议使用环境变量 DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://db_4m_user:xiOe63X4iaczwTAcNfUYwS8oWrDExkHX@dpg-d11rb03uibrs73eh87vg-a/db_4m")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
