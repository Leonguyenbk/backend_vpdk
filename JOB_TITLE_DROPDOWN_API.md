# Job Title Dropdown API Documentation

## Overview
Backend đã được cập nhật để hỗ trợ chọn chức danh từ dropdown thay vì nhập text. Điều này giúp chuẩn hóa dữ liệu và tránh lỗi nhập liệu.

## New API Endpoints

### 1. GET /api/admin/job-titles
Lấy danh sách chức danh cho dropdown.

**Authentication:** Required (Admin JWT token)

**Response:**
```json
[
  {
    "id": 1,
    "code": "GD_VP",
    "name": "Giám đốc Văn phòng",
    "level_no": 5,
    "is_manager": true,
    "data_scope": "all",
    "is_active": true,
    "created_at": "2026-03-09T09:10:24.573318"
  },
  {
    "id": 5,
    "code": "TP",
    "name": "Trưởng phòng",
    "level_no": 4,
    "is_manager": true,
    "data_scope": "subtree",
    "is_active": true,
    "created_at": "2026-03-09T09:10:24.573318"
  }
]
```

**Notes:**
- Chỉ trả về các chức danh đang active (`is_active = true`)
- Sắp xếp theo `level_no` giảm dần, sau đó `name` tăng dần
- Frontend có thể sử dụng `id`, `name`, và `code` cho dropdown

### 2. PUT /api/admin/users/{user_id}
Cập nhật user với chức danh từ dropdown.

**Authentication:** Required (Admin JWT token)

**Request Body (mới):**
```json
{
  "job_title_id": 5,  // ID từ dropdown (có thể null)
  "full_name": "Nguyễn Văn A",
  "email": "nguyenvana@example.com",
  // ... other fields
}
```

**Validation:**
- `job_title_id` phải là số nguyên hoặc null
- Nếu không null, phải tồn tại trong bảng `job_title` và `is_active = true`
- Nếu không hợp lệ, trả về lỗi 400: "Chuc danh khong ton tai hoac da bi vo hieu hoa"

## Backward Compatibility
- Vẫn hỗ trợ `job_title` text field (không bắt buộc)
- API response vẫn bao gồm cả `job_title` (legacy) và `job_title_id` + `job_title_name` (mới)

## Frontend Implementation

### 1. Load Job Titles for Dropdown
```javascript
// React example
const [jobTitles, setJobTitles] = useState([]);

useEffect(() => {
  fetch('/api/admin/job-titles', {
    headers: { Authorization: `Bearer ${token}` }
  })
  .then(res => res.json())
  .then(data => setJobTitles(data));
}, []);
```

### 2. Render Dropdown
```javascript
// React Select example
<Select
  options={jobTitles.map(jt => ({
    value: jt.id,
    label: `${jt.code} - ${jt.name}`,
    level: jt.level_no
  }))}
  onChange={(selected) => setUserData({...userData, job_title_id: selected?.value || null})}
/>
```

### 3. Submit Form
```javascript
const handleSubmit = () => {
  fetch(`/api/admin/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      ...userData,
      job_title_id: selectedJobTitleId  // Send the ID instead of text
    })
  });
};
```

## Migration Notes
- Database đã được migrate với bảng `job_title` mới
- 10 chức danh mặc định đã được seed
- Không ảnh hưởng đến dữ liệu hiện có

## Testing
Chạy file `test_dropdown.py` để verify functionality:
```bash
python test_dropdown.py
```