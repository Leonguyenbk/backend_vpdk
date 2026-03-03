import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@localhost/qlns_vpdk?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'baomat_sieucap_vjp_pro_2026_ql_nhansu_vpdk_2026'
    JWT_ACCESS_TOKEN_EXPIRES = False