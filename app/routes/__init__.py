from .auth_routes import auth_bp
from .admin_users import admin_users_bp   # ✅ thêm dòng này

all_blueprints = [
    (auth_bp, '/api/auth'),
    (admin_users_bp, '/api/admin/users'),   # ✅ thêm vào đây
]