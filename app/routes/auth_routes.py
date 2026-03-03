from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import User
from werkzeug.security import check_password_hash
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # 1. Lấy dữ liệu từ React gửi lên
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    password = data.get('password')

    # 2. Kiểm tra tài khoản trong MySQL
    user = User.query.filter_by(username=username).first()

    # 3. So sánh mật khẩu đã hash
    if user and check_password_hash(user.password_hash, password):
        # Tạo JWT Token (Không hết hạn theo config của ông)
        # Identity thường để ID của user để sau này truy vấn ngược lại
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role} # Gửi kèm role để React phân quyền UI
        )
        
        return jsonify({
            "status": "success",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value  # Lấy giá trị của Enum để gửi về React
            }
        }), 200

    # 4. Sai thông tin
    return jsonify({"status": "error", "msg": "Tài khoản hoặc mật khẩu không chính xác"}), 401