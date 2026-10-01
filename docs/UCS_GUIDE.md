# Hoàn thiện phần UCS — Huy — 01/10/2026

## Cài bản cập nhật

Gói Sokoban_UCS_Update.zip chứa 3 file theo đúng đường dẫn tương đối của Sokoban_Starter:

- source/task1/sokoban/search/ucs.py — thay file UCS cũ.
- tests/test_ucs.py — thêm kiểm thử riêng cho UCS.
- docs/UCS_GUIDE.md — hướng dẫn này.

Giải nén gói ra một thư mục tạm, rồi chép các thư mục source/tests/docs bên trong vào thư mục Sokoban_Starter đang có. Chấp nhận thay ucs.py. Không đặt thêm một thư mục source bên trong source. Không chạy ucs.py trực tiếp vì dùng relative imports; chạy main.py từ thư mục gốc.

Code UCS được viết theo giả mã môn học và giao diện của khung; chưa nhận file Python mẫu của nhóm. Chỉ phần UCS đã được hoàn thiện trong lần này. Các ghi chú “UCS chưa triển khai” ở tài liệu của bản khung cũ được thay thế bởi hướng dẫn này. A*, heuristic và cạnh tranh vẫn giữ trạng thái chưa hoàn thiện.

## Cách chạy bằng môi trường của bạn

Mở PowerShell tại D:\TDTU\Introduction AI\Sokoban_Starter. Dùng .venv đã tạo bằng Python 3.13; không cần tạo lại.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/tiny.txt
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/two_boxes.txt
.\.venv\Scripts\python.exe main.py --map maps/single/two_boxes.txt
```

GUI: nhấn 1 chọn UCS, Enter tìm lời giải từ trạng thái ban đầu, Space để phát/tạm dừng, → tiến, ← lùi. Lời giải mới được nạp ở trạng thái tạm dừng nên không tự chạy cho đến khi nhấn Space hoặc →.

## Luồng thuật toán

1. Đặt deadline; khởi tạo frontier bằng trạng thái đầu với g=0.
2. best_g lưu chi phí thấp nhất đã biết của mỗi trạng thái; parents lưu trạng thái cha và hành động.
3. Lấy entry có g nhỏ nhất từ heap.
4. Nếu entry cũ có g khác best_g, bỏ qua.
5. Nếu là đích, lần theo parents, đảo chuỗi hành động và trả SOLVED.
6. Nếu hết giới hạn mở rộng, trả LIMIT_REACHED.
7. Sinh các trạng thái kế tiếp qua core.rules.successors.
8. Chỉ khi chi phí mới thấp hơn best_g mới cập nhật cha, chi phí và thêm heap entry.
9. Nếu heap cạn, trả UNSOLVABLE. Nếu chạm deadline khi còn đang tìm, trả TIMEOUT.

## Vì sao viết như vậy?

- Heap entry `(cost, counter, state)`: counter phân xử hòa, tránh Python so sánh hai State không có thứ tự.
- Dùng best_g thay cho chỉ visited: có thể tiếp nhận một đường tốt hơn. Chỉ giữ đường đầu tiên gặp không đúng cho bài toán chi phí tổng quát.
- Không xóa trực tiếp entry cũ trong heap: thêm entry mới rồi bỏ entry lỗi thời khi lấy ra. Đây là cách thực hiện cập nhật ưu tiên bằng heapq.
- Kiểm tra đích khi lấy ra: một đích mới sinh có thể còn có đường khác rẻ hơn.
- Chi phí trong khung là 1 cho mỗi hành động hợp lệ. UCS vì vậy cho số bước tối thiểu; đẩy là một hành động, không cộng riêng bước người.
- Bộ đếm expanded chỉ tăng khi thực sự mở rộng một trạng thái không phải đích và không lỗi thời. generated đếm các successor hợp lệ được sinh, kể cả trùng. max_frontier tính heap entry vật lý; max_reached tính số state trong best_g. preprocess_ms=0 vì UCS không có tiền xử lý heuristic.
- TIMEOUT/LIMIT_REACHED không chứng minh vô nghiệm. Khi một lời giải đã vào heap và được lấy ra ngay sau lần mở rộng cuối cùng được phép, có thể trả SOLVED mà không mở rộng thêm.
- Deadline là kiểm tra hợp tác trong vòng lặp, không phải bộ cưỡng chế thời gian thực. Việc dựng đường đi/dọn bộ nhớ có thể làm tổng thời gian nhỉnh hơn budget. Không dùng cơ chế này thay runner timeout cho hai tác tử.

## Kết quả xác minh

Môi trường thực tế: Linux, Python 3.12.14, pygame 2.6.1. Chưa kiểm tra Windows Python 3.13 hoặc Mac Intel thật.

- Tổng 21 test pass: 12 test nền tảng và 9 test UCS.
- tiny: SOLVED, [East], cost=1.
- already_solved: SOLVED, [], cost=0.
- two_boxes: SOLVED, cost=8; chuỗi East, East, East, West, West, South, East, East. Phát lại đến đích. Trong lần kiểm tra: expanded=284, generated=925, max_frontier=209, max_reached=492.
- unsolvable: UNSOLVABLE sau khi frontier cạn.
- Giới hạn một expansion trên two_boxes: LIMIT_REACHED.
- Đồng hồ giả lập vượt deadline: TIMEOUT, không có lời giải giả.
- Toàn bộ 72 trạng thái người/thùng không trùng nhau trên một map 3x3 nền được đối chiếu với BFS độc lập về cơ chế hàng đợi; chi phí và trạng thái kết quả khớp. Cả hai dùng chung luật trò chơi đã kiểm tra riêng.
- Đồ thị có trọng số giả lập: xác nhận cập nhật đường tốt hơn, bỏ heap entry cũ, không dừng ở đích vừa sinh; kết quả 12 thay vì 20.
- GUI headless: gửi Enter qua event pygame, nhận lời giải two_boxes gồm 8 hành động và 9 snapshot, trạng thái cuối là đích.
- Map reference với max_expanded=20000 và seconds=2: LIMIT_REACHED tại 20000, không kết luận map vô nghiệm. UCS thuần có thể tốn nhiều bộ nhớ/thời gian với nhiều thùng.

Các test nhỏ là bằng chứng kiểm tra, không phải tuyên bố mọi map đều giải được trong giới hạn. Chưa thêm heuristic, deadlock pruning hoặc gộp bước đẩy để giữ baseline UCS rõ ràng khi so với A*.

## Kiểm tra thêm trên máy của bạn

```powershell
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/already_solved.txt
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/unsolvable.txt
.\.venv\Scripts\python.exe main.py --mode solve --algorithm ucs --map maps/single/two_boxes.txt --max-expanded 1
```

Mong đợi lần lượt solved cost=0, unsolvable, limit_reached. CLI trả exit code 2 cho các trường hợp không solved theo khung, không đồng nghĩa Python crash. Benchmark so sánh hai thuật toán chưa chạy hoàn chỉnh vì A* chưa triển khai; không sửa A* để trả kết quả giả.

## Nội dung để vấn đáp

Bạn phải tự giải thích được frontier, best_g, parents, counter, bỏ entry cũ, goal-on-pop, và phân biệt 4 trạng thái kết quả. Với cost=1, UCS tương đương BFS về ưu tiên theo tầng/chi phí nhưng vẫn đang được cài bằng hàng đợi ưu tiên theo đề. Tính tối ưu dựa trên chi phí dương, lấy g nhỏ nhất và cập nhật đường tốt hơn; khi bị cắt bởi giới hạn thì không bảo đảm trả được nghiệm.
