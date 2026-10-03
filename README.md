# Sokoban — bản tích hợp nhóm 3 người

**Hạn nộp: 17:00 ngày 05/10/2026, giờ Việt Nam. Code đã tích hợp; nhóm vẫn cần nghiệm thu trên máy đích và hoàn thiện hồ sơ nộp.**

| MSSV | Họ tên | Vai trò |
|---|---|---|
| 524H0091 | Phạm Minh Huy | Lõi luật, UCS, engine cạnh tranh, AgentOne |
| 524H0026 | Lưu Minh Phương | A*, heuristic, kiểm chứng, AgentTwo |
| 524H0084 | Phan Hồng Đăng | pygame, benchmark, tích hợp GUI, đóng gói |

Mỗi người phải đọc, sửa, kiểm tra và giải thích phần mình; lưu nguồn code mẫu và các quyết định thực tế. Không tự điền số liệu hay tỷ lệ hoàn thành chưa có bằng chứng.

## 1. Chạy trên Windows

Mở thư mục chứa `main.py` bằng VS Code. Nhóm sử dụng Python 3.13 64-bit và pygame 2.6.1.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Không bắt buộc activate môi trường nên tránh được lỗi ExecutionPolicy của PowerShell. VS Code: Ctrl+Shift+P → Python: Select Interpreter → chọn `.venv\Scripts\python.exe`.

Nếu `py -3.13` báo không tìm thấy: dùng `py -0p` để xem Python đã cài. Cài Python 3.13 hoặc thống nhất phiên bản khác trước khi tạo môi trường, không tự chuyển phiên bản riêng từng thành viên.

### Thao tác hiện có

- Space: phát/tạm dừng lịch sử; → tiến; ← lùi.
- R: đặt lại trạng thái ban đầu.
- 1: chọn UCS; 2: chọn A*; Enter: gọi solver từ trạng thái ban đầu.
- Trong lúc solver chạy, không nhận thêm lệnh giải hoặc đổi thuật toán.
- Kết quả được phát lại bằng Space hoặc phím mũi tên; đóng cửa sổ sẽ yêu cầu dừng tác vụ nền.

Chọn map:

```powershell
.\.venv\Scripts\python.exe main.py --map maps/single/two_boxes.txt
.\.venv\Scripts\python.exe main.py --mode validate --map maps/single/reference_transcribed.txt
.\.venv\Scripts\python.exe main.py --mode validate --competitive-map --map maps/competitive/arena.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Giải bài và đo hiệu năng:

```powershell
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/tiny.txt
.\.venv\Scripts\python.exe main.py --mode solve --algorithm astar --map maps/single/tiny.txt
.\.venv\Scripts\python.exe main.py --mode benchmark --map maps/single/two_boxes.txt --repeats 3 --output results/two_boxes.csv
```

Kiểm chứng heuristic và chạy hai tác tử thật:

```powershell
.\.venv\Scripts\python.exe main.py --mode verify --map maps/single/two_boxes.txt --verify-states 50
.\.venv\Scripts\python.exe main.py --mode compete --map maps/competitive/arena.txt --rounds 8 --agent-two agent-two
.\.venv\Scripts\python.exe main.py --mode competitive-gui --map maps/competitive/arena.txt --rounds 50 --agent-two agent-two
```

GUI thi đấu: Enter bắt đầu, Space phát/tạm dừng **phần xem lại**, phím mũi tên tiến/lùi. Bộ chạy trận tiếp tục thu kết quả nền khi phần xem lại tạm dừng. R về lượt 0 sau khi trận tính xong. Đóng cửa sổ dừng worker. AgentTwo là mặc định của CLI/GUI; `--agent-two wait` chỉ dùng kiểm thử với đối thủ đứng yên.

`verify` chỉ kiểm tra mẫu: trạng thái không có chi phí tối ưu hữu hạn vẫn được kiểm tra consistency; nếu không có mẫu admissibility thì trả `inconclusive` và exit code 2.

## 2. Bản đồ và quy ước

Theo đề: `%` tường, `A` người chơi, `B` thùng, `D` đích, `C` thùng trên đích, dấu cách là nền. Mở rộng riêng cho thi đấu: `P` là tác tử thứ hai. Tệp UTF-8, không tab; giữ nguyên khoảng trắng. Parser yêu cầu các đối tượng nằm trong vùng kín và số thùng bằng số đích, lớn hơn 0.

`reference_transcribed.txt` được chép theo ảnh đã gửi, **chưa khẳng định là bản chính thức hay đã giải được**. Các map tiny/two_boxes phục vụ kiểm tra trước. Không dùng chỉ một map nhỏ để kết luận hiệu năng.

## 3. Cấu trúc chính

| Thư mục | Vai trò |
|---|---|
| `source/task1/sokoban/core` | Trạng thái, đọc map, luật, lịch sử |
| `source/task1/sokoban/search` | UCS/A*, heuristic, kết quả chuẩn |
| `source/task1/sokoban/competitive` | Giao diện tác tử, engine, runner |
| `source/task1/sokoban/ui` | GUI pygame |
| `source/task1/sokoban/experiments` | Benchmark và kiểm tra heuristic |
| `maps` | Map một tác tử và hai tác tử |
| `tests` | Kiểm tra nền tảng; không chứng nhận các TODO |
| `results` | Kết quả thực nghiệm thực tế sẽ được tạo sau |
| `submission` | Hướng dẫn đóng gói cuối, chưa phải bản nộp |

## 4. Trạng thái bản tích hợp

Đã có: parser, trạng thái bất biến, UCS, A*, heuristic BFS trên đồ thị sàn, replay GUI, engine cạnh tranh, AgentOne, AgentTwo, runner cách ly tiến trình với giới hạn quyết định 1000 ms, GUI cạnh tranh, benchmark và kiểm chứng mẫu heuristic.

Bản kiểm tra ngày 02/10: **85 tests đạt** trên Linux/Python 3.12.14/pygame 2.6.1. Có test A*, AgentTwo, replay GUI, hai controller thật, timeout và dọn worker. Đây chưa phải xác nhận chạy thực tế trên Windows/Python 3.13 hoặc Mac Intel.

Cần hoàn thiện: benchmark trên nhiều map và máy dùng để trình bày; báo cáo đầy đủ; slide PDF; video; kiểm tra máy đích. Map `reference_transcribed.txt` chưa được chứng nhận có lời giải.


## 5. Cập nhật tích hợp ngày 03/10/2026

Ghép bản dự án đầy đủ với `feature/gui-benchmark` tại commit `b7fb619`.
Giữ sửa lỗi pause/replay, chống gọi Solve trùng, thoát smoke, hủy solver/worker,
kiểm chứng heuristic và AgentTwo trong bản dự án đầy đủ.

Bổ sung từ nhánh GUI: nhập số lượt trực tiếp (gõ số rồi Enter), phím T đổi đối thủ,
lưu log trận bằng `--match-output`, benchmark nhiều map và CSV tổng hợp,
phân tích log trận. AgentTwo vẫn là đối thủ mặc định.

```powershell
python main.py --mode benchmark --maps maps/single/tiny.txt maps/single/two_boxes.txt --repeats 3 --output results/benchmark.csv
python main.py --mode competitive-gui --map maps/competitive/arena.txt --rounds 50 --match-output results/match.json
python main.py --mode analyze-match --match-input results/match.json --analysis-output results/match_analysis.json
```

Thư mục `docs/` giữ các hướng dẫn và tài liệu tham khảo từ nhánh nhóm; các ghi chú
trạng thái cũ trong đó không thay thế trạng thái của bản tích hợp trong README này.

Kiểm tra bản ghép: 88 tests đạt trên Linux/Python 3.12 với pygame 2.6.1 (SDL dummy). Benchmark nhiều map và phân tích log chạy thành công. Chưa xác nhận trên macOS Intel.

GUI đơn hiển thị tổng Actions/Cost của lời giải, tách khỏi Replay (bước đang xem). Tiến/lùi không thay đổi tổng chi phí.
