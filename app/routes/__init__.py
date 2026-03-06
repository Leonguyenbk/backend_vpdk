from .admin_users import admin_users_bp
from .auth_routes import auth_bp
from .manager_routes import manager_bp


all_blueprints = [
    (auth_bp, "/api/auth"),
    (admin_users_bp, "/api/admin"),
    (manager_bp, "/api/manager"),
]
