# Đây chưa phải gói nộp

ZIP khung dùng để phát triển; không đổi tên ZIP này rồi nộp ngay.

Khi hoàn tất, tạo từng folder theo `AI_midterm_<mã nhóm thật>_<MSSV>`. Mã nhóm hiện chưa được cung cấp. Cả ba đều phải nộp, chỉ khác MSSV trong tên folder theo đề.

Trong folder cuối:

- `source/`: project chạy được, giữ subfolder `task1` chứa mã Sokoban; đưa main.py, maps, requirements và hướng dẫn chạy cùng project, điều chỉnh ROOT/đường dẫn nhất quán nếu di chuyển.
- `presentation.pdf`: slide hoàn chỉnh tỷ lệ 4:3.
- `demo.txt`: URL video thật tối đa 3 phút, quyền xem đúng.
- `report.pdf` hoặc `report.docx`: báo cáo bổ sung theo định dạng giảng viên chấp nhận; tên này là đề xuất, không phải tên bắt buộc trong PDF đề.

Do task 2 là trình bày, presentation.pdf nằm ở root theo đề. Nếu giảng viên còn yêu cầu tài liệu nguồn của slide trong thư mục task riêng, thêm `source/task2/`; không tự nhận đây là yêu cầu đã xác nhận.

Lưu ý main.py của khung tìm package tại `ROOT/source/task1`. Khi chuyển toàn bộ thư mục khung vào source cuối, vẫn giữ đúng cấu trúc bên trong hoặc sửa bootstrap rồi chạy kiểm tra ở thư mục giải nén mới. Đừng di chuyển mỗi file main.py mà quên package/map.
