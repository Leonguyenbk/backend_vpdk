from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors
from .routes import all_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các tiện ích
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Cấu hình CORS để React (port 3000) gọi được Flask (port 5000)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Đăng ký các Route
    for bp, prefix in all_blueprints:
        app.register_blueprint(bp, url_prefix=prefix)

    return app