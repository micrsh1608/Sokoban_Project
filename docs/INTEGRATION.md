# Chuẩn tích hợp

## UCS/A*: gửi code mẫu trước khi sửa sâu

Chưa nhận code mẫu từ nhóm nên hai solver là adapter chưa triển khai, không phải chuyển đổi từ code mẫu đã có. Đặt code gốc ở bản lưu riêng để đối chiếu và ghi nguồn được phép sử dụng; không nhập nguyên module có lệnh demo tự chạy khi import.

Mỗi solver giữ đúng chữ ký:

`solve(board: Board, initial: State, limits: SearchLimits) -> SearchResult`

- Dùng `successors(board, state)`, không đọc map hoặc pygame trong solver.
- `State` là hashable; best_g và parent có thể dùng State làm key.
- UCS ưu tiên g; A* ưu tiên g+h. Khi f bằng nhau, heap cần counter để không cố so sánh các đối tượng State.
- Chỉ bỏ entry cũ khi biết g của entry không còn là best_g; quản lý việc cập nhật đường tốt hơn.
- Kiểm tra đích khi lấy trạng thái phù hợp từ hàng đợi, không dừng ngay khi mới sinh đích.
- Với trạng thái đầu đã là đích: actions=(), total_cost=0, status=SOLVED.
- Dựng chuỗi hành động đúng thứ tự từ cha; không chỉ trả danh sách vị trí thùng.
- UNSOLVABLE chỉ dùng khi đã duyệt hết không gian liên quan một cách đầy đủ.
- TIMEOUT/LIMIT_REACHED khác UNSOLVABLE; không gán chi phí 0 hay vô cực thành nghiệm.
- Dùng perf_counter, kiểm tra deadline trong vòng lặp. GUI chạy solver ở thread để cửa sổ vẫn xử lý sự kiện; thread không thể cưỡng bức dừng solver treo.
- `validate_result` xác minh chuỗi hành động và chi phí trước khi hiển thị/chấp nhận benchmark.

## Định nghĩa metrics dùng chung

- expanded: số lần thực sự sinh successors từ entry không cũ; không tính trạng thái đích nếu trả ngay.
- generated: số successor hợp lệ được sinh, kể cả trùng trạng thái.
- max_frontier: số entry vật lý lớn nhất trong heap, kể cả entry cũ chưa lấy ra.
- max_reached: số key lớn nhất trong best_g.
- preprocess_ms: thời gian xây dữ liệu heuristic trong mỗi lần gọi solver.
- elapsed_ms do benchmark đo bao quanh toàn bộ solve nên đã bao gồm tiền xử lý.

Không cộng thời gian vẽ/hoạt ảnh vào tìm kiếm. Benchmark dùng một lần chạy không tracemalloc để đo thời gian và một lần có tracemalloc để đo bộ nhớ Python. Cột memory_run_status/cost để nhận diện việc run đo bộ nhớ bị timeout khác với run đo thời gian. Tracemalloc không phải toàn bộ RAM tiến trình. Không báo số node là byte RAM.

Các solver không cache dữ liệu map qua các run nếu muốn benchmark cold-start như hiện tại. Nếu thêm cache, tách thí nghiệm warm/cold và ghi cách reset. Khi mở rộng benchmark nhiều map, đầu ra mỗi map đặt tên riêng hoặc bổ sung runner gộp có cột map; không vô tình ghi đè kết quả cũ.

## Heuristic và kiểm chứng

Không dùng Euclidean/Manhattan. Chọn cách ước lượng cùng đơn vị chi phí; viết lập luận trước khi khẳng định tối ưu. Tránh cộng hai cận dưới một cách tùy tiện làm tính trùng chi phí.

`Heuristic(board)` là vị trí tiền xử lý; `heuristic(state)` trả số. Phương chịu trách nhiệm cài đặt và giải thích. Không để hàm h=0 rồi báo đã hoàn thành yêu cầu đề xuất heuristic có ý nghĩa mà chưa thảo luận.

`check_samples(board, heuristic, exact_costs)` đã có bộ kiểm tra mẫu; nhóm cần bổ sung bộ tạo dữ liệu `State -> optimal_remaining_cost` trên map nhỏ, thu từ bộ giải tối ưu độc lập với heuristic cần kiểm tra. Có thể dùng UCS đã kiểm tra đúng, hoặc duyệt đầy đủ đồ thị trạng thái nhỏ rồi tìm khoảng cách về tập đích qua cạnh đảo.

- Ghi cách lấy mẫu, số trạng thái, số cạnh, số map, số vi phạm.
- Chỉ đưa chi phí hữu hạn đã xác định chính xác vào exact_costs. Timeout không phải một kết quả chính xác.
- Bộ checker hiện xét trạng thái có nghiệm trong tập mẫu và các cạnh đi ra từ đó. Muốn tuyên bố kiểm tra đầy đủ một đồ thị, phải bổ sung xử lý/trình bày các trạng thái không có nghiệm và phạm vi bao phủ.
- Không dùng chính A* chưa xác minh làm nguồn h* rồi kết luận h là admissible.
- Chưa có dataset và kết quả thì không ghi yêu cầu 4 hoàn thành.

## Phụ thuộc giữa ba người

Huy chốt model/parser/rules/contracts → Phương cài solver và heuristic; Đăng dùng model/history và registry. Huy cài engine joint step → hai agent dùng engine để mô phỏng; Đăng dựng GUI cạnh tranh. Hai solver chạy đúng → Đăng chạy benchmark; Phương chạy oracle để kiểm chứng.

Đăng có thể phát triển GUI trên map nhỏ ngay mà không chờ thuật toán. Phương có thể làm việc với lõi một tác tử đã có. Mỗi người tránh sửa file của người khác khi chưa trao đổi. Mỗi commit tập trung một thay đổi; chạy tests trước ghép.
