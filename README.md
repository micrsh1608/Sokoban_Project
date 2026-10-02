# Sokoban — khung dự án nhóm 3 người

**Hạn nộp: 17:00 ngày 05/10/2026, giờ Việt Nam. Đây là khung để phát triển, chưa phải bài hoàn chỉnh để nộp.**

| MSSV | Họ tên | Vai trò |
|---|---|---|
| 524H0091 | Phạm Minh Huy | Lõi luật, UCS, engine cạnh tranh, AgentOne |
| 524H0026 | Lưu Minh Phương | A*, heuristic, kiểm chứng, AgentTwo |
| 524H0084 | Phan Hồng Đăng | pygame, benchmark, tích hợp GUI, đóng gói |

Nhóm xác nhận giảng viên cho phép dùng AI với điều kiện hiểu nội dung. Mỗi người phải đọc, sửa, kiểm tra và giải thích phần mình; lưu nguồn code mẫu và các quyết định thực tế. Không tự điền số liệu hay tỷ lệ hoàn thành chưa có bằng chứng.

## 1. Chạy trên Windows

Mở thư mục chứa `main.py` bằng VS Code. Khuyến nghị Python 3.11 64-bit, pygame 2.6.1. Nếu đã dùng Python khác, cả nhóm phải thống nhất và kiểm tra cùng một phiên bản.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Không bắt buộc activate môi trường nên tránh được lỗi ExecutionPolicy của PowerShell. VS Code: Ctrl+Shift+P → Python: Select Interpreter → chọn `.venv\Scripts\python.exe`.

Nếu `py -3.11` báo không tìm thấy: dùng `py -0p` để xem Python đã cài. Cài Python 3.11 hoặc thống nhất phiên bản khác trước khi tạo môi trường, không tự chuyển phiên bản riêng từng thành viên.

### Thao tác hiện có

- WASD: chơi thủ công để kiểm tra luật; đây là tiện ích bổ sung.
- Space: phát/tạm dừng lịch sử; → tiến; ← lùi.
- R: đặt lại trạng thái ban đầu.
- 1: chọn UCS; 2: chọn A*; Enter: gọi solver từ trạng thái ban đầu.
- **Hiện Enter trả `not_implemented` vì chưa ghép code mẫu. Đây là trạng thái có chủ ý.**

Chọn map:

```powershell
.\.venv\Scripts\python.exe main.py --map maps/single/two_boxes.txt
.\.venv\Scripts\python.exe main.py --mode validate --map maps/single/reference_transcribed.txt
.\.venv\Scripts\python.exe main.py --mode validate --competitive-map --map maps/competitive/arena.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Sau khi Huy/Phương ghép thuật toán:

```powershell
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/tiny.txt
.\.venv\Scripts\python.exe main.py --mode solve --algorithm astar --map maps/single/tiny.txt
.\.venv\Scripts\python.exe main.py --mode benchmark --map maps/single/two_boxes.txt --repeats 3 --output results/two_boxes.csv
```

Lệnh `--mode compete --map maps/competitive/arena.txt --rounds 50` và `--mode verify` hiện báo rõ phần chưa triển khai. Không demo các lệnh này như chức năng đã hoàn tất.

## 2. Bản đồ và quy ước

Theo đề: `%` tường, `A` người chơi, `B` thùng, `D` đích, `C` thùng trên đích, dấu cách là nền. Mở rộng riêng cho thi đấu: `P` là tác tử thứ hai. Tệp UTF-8, không tab; giữ nguyên khoảng trắng. Parser yêu cầu các đối tượng nằm trong vùng kín và số thùng bằng số đích, lớn hơn 0.

`reference_transcribed.txt` được chép theo ảnh đã gửi, **chưa khẳng định là bản chính thức hay đã giải được**. Các map tiny/two_boxes phục vụ kiểm tra trước. Không dùng chỉ một map nhỏ để kết luận hiệu năng.

## 3. Tệp cần đọc trước

1. `docs/PLAN_AND_OWNERS.md`: công việc và lịch đến 05/10.
2. `docs/DECISIONS.md`: luật nhóm chọn cho các chỗ đề chưa nói chi tiết.
3. `docs/INTEGRATION.md`: chuẩn ghép UCS/A*/GUI/tác tử.
4. `docs/REPORT_TEMPLATE.md`: khung báo cáo tiếng Việt, có mục chưa hoàn thành.
5. `docs/ACCEPTANCE.md`: tiêu chí nghiệm thu và nộp bài.
6. `docs/ENVIRONMENT.md`: giới hạn xác nhận Windows/macOS.
7. `docs/VERIFICATION.md`: kết quả kiểm tra chính khung này.
8. `docs/COURSE_ALIGNMENT.md`: đối chiếu UCS/A* với hai slide môn học vừa nhận.

## 4. Cấu trúc chính

| Thư mục | Vai trò |
|---|---|
| `source/task1/sokoban/core` | Trạng thái, đọc map, luật, lịch sử |
| `source/task1/sokoban/search` | UCS/A*, heuristic, kết quả chuẩn |
| `source/task1/sokoban/competitive` | Giao diện tác tử, engine, runner |
| `source/task1/sokoban/ui` | GUI pygame |
| `source/task1/sokoban/experiments` | Benchmark và kiểm tra heuristic |
| `maps` | Map một tác tử và hai tác tử |
| `tests` | Kiểm tra nền tảng; không chứng nhận các TODO |
| `docs` | Phân công, quy ước, báo cáo và checklist |
| `results` | Kết quả thực nghiệm thực tế sẽ được tạo sau |
| `submission` | Hướng dẫn đóng gói cuối, chưa phải bản nộp |

## 5. Trạng thái thật của khung

Đã có: parser, trạng thái bất biến, luật một tác tử, chi phí đơn vị, GUI thủ công/replay, hợp đồng solver, kiểm tra lời giải, bộ chạy benchmark, hàm kiểm tra mẫu heuristic và giao diện tác tử.

Chưa có: UCS/A* tích hợp, heuristic, bộ dữ liệu chi phí tối ưu, engine chuyển trạng thái đồng thời, agent tìm kiếm, runner timeout, GUI cạnh tranh, số liệu thực nghiệm, báo cáo hoàn chỉnh, slide PDF, video và kiểm tra thực tế trên Mac Intel.

Tìm `TODO`, `NotImplementedError` và `NOT_IMPLEMENTED` để nhận diện các điểm cần hoàn thiện. Không đổi chúng thành kết quả giả để làm chương trình trông như hoàn tất.
