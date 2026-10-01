# Kiểm tra bản khung — 01/10/2026

Môi trường kiểm tra thực tế: Linux, CPython 3.12.14, pygame 2.6.1, SDL 2.28.4. Chưa kiểm tra Windows hoặc macOS bằng máy thật; Python 3.11 là phiên bản đề xuất cho nhóm, khác phiên bản runtime dùng kiểm tra này.

## Kết quả đã thực hiện

- `python -m unittest discover -s tests -v`: **12/12 pass**.
- Bao gồm: đẩy đến đích, C giữ đích sau khi thùng rời đi, cấm đẩy hai thùng, cấm xuyên tường/Wait ở single, từ chối map hở, map không chữ nhật, replay/nhánh lịch sử, từ chối lời giải sai, đích ban đầu, khóa vị trí thùng không phụ thuộc thứ tự, phát lại lời giải tự kiểm tra cho map two_boxes, khởi tạo cạnh tranh.
- Parser map chép theo ảnh: 1 tác tử, 7 thùng, 7 đích; không nhận vùng trống ngoài làm sàn.
- Parser arena: 2 tác tử, 2 thùng, 2 đích.
- GUI: SDL dummy khởi tạo pygame, vẽ một frame rồi thoát thành công; đã xem ảnh render map reference và các dòng điều khiển, không bị cắt ở kích thước kiểm tra.
- CLI solve UCS/A*: trả `not_implemented`, exit 2 đúng chủ ý.
- CLI compete/verify: thông báo chưa triển khai, exit 2 đúng chủ ý.
- CLI benchmark với solver chưa tích hợp: từ chối tạo CSV số liệu, exit 2.
- Giới hạn thời gian NaN: từ chối với exit 2.

## Phạm vi chưa kiểm tra/chưa có

- Chưa có kết quả tìm kiếm UCS/A*, vì mới có adapter.
- Chưa chứng minh hoặc kiểm chứng heuristic cụ thể.
- Chưa có joint transition, runner hay agent hoạt động; test khởi tạo không chứng nhận gameplay.
- Chưa có GUI cạnh tranh và chưa kiểm tra tương tác bàn phím trên Windows/Mac thật.
- Chưa giải map reference bằng solver; chỉ xác nhận parser và bố cục.
- Chưa có benchmark hoàn chỉnh, slide/video hoặc báo cáo kết quả cuối.

Không diễn giải 12 tests pass thành hoàn thành 8/8 yêu cầu của đề. Cập nhật tài liệu này khi nhóm bổ sung kiểm thử thực tế.
