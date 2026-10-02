## 1. Phạm vi đã làm

- `search/astar.py`: A* graph search, `f = g + h`, `best_g`, parent links, stale-entry skipping, reopen khi có đường đi tốt hơn, deadline và expansion limit.
- `search/heuristics.py`: heuristic dựa trên khoảng cách đường đi ngắn nhất trên **đồ thị ô sàn** từ mỗi thùng đến đích gần nhất. Không dùng Manhattan/Euclidean.
- `experiments/verify_heuristic.py`: sinh mẫu trạng thái reachable, dùng UCS làm oracle chi phí tối ưu, kiểm tra admissibility và consistency.
- `cli.py`: bổ sung `--mode verify` để chạy kiểm chứng trực tiếp.
- `competitive/agent_two.py`: AgentTwo dùng A* để tìm chuỗi hành động ngắn cải thiện chênh lệch điểm, tái lập kế hoạch mỗi lượt, có deadline và node limit.
- `tests/test_astar.py`, `tests/test_agent_two.py`: kiểm thử phần mới.

## 2. Heuristic

Với trạng thái `s`, với mỗi box `b`, tính:

`d(b) = min khoảng cách BFS trên đồ thị floor từ b đến một goal`.

Heuristic:

`h(s) = Σ d(b)`.

Các box khác và khả năng người chơi tiếp cận bị bỏ qua khi tính `d`, nên đây là một cận dưới: mỗi box trong lời giải thật phải được đẩy ít nhất `d(b)` lần, còn tổng số action luôn không nhỏ hơn tổng số push.

### Admissibility

`h(s) ≤ h*(s)` vì mỗi thành phần `d(b)` là số push tối thiểu nếu bỏ qua các ràng buộc khó hơn của Sokoban. Heuristic không trả vô cực cho component không có goal; contribution của component đó là `0`, nên vẫn là cận dưới hữu hạn.

### Consistency

- Nếu action chỉ di chuyển người: vị trí box không đổi ⇒ `h` không đổi.
- Nếu action đẩy một box sang ô kề: khoảng cách ngắn nhất của box đó đến goal thay đổi nhiều nhất 1 ⇒ `h(s) ≤ 1 + h(s')`.
- Chỉ một box được đẩy trong một action và cost của action là 1.

Do đó heuristic có tính nhất quán theo quy ước cost=1 của nhóm. Khi trạng thái đích đạt được, tất cả box nằm trên goal nên `h(goal)=0`.

## 3. Chạy A*

Từ thư mục project:

```powershell
python main.py --mode solve --algorithm astar --map maps/single/tiny.txt
python main.py --mode solve --algorithm astar --map maps/single/two_boxes.txt
```

Benchmark:

```powershell
python main.py --mode benchmark --map maps/single/two_boxes.txt --repeats 3 --seconds 5 --max-expanded 100000 --output results/benchmark_two_boxes.csv
```

Kiểm chứng heuristic:

```powershell
python main.py --mode verify --map maps/single/two_boxes.txt --verify-states 50 --seconds 2 --max-expanded 100000
```

## 4. AgentTwo

AgentTwo nhận cùng `Observation` và dùng `CompetitionEngine.resolve()` để mô phỏng, không tự viết lại luật cạnh tranh.

Cách hoạt động:

1. Lấy điểm hiện tại làm mốc.
2. Dùng A* tìm các trạng thái khi chỉ AgentTwo hành động và đối thủ được mô phỏng là `Wait`.
3. `g` là số lượt mô phỏng; heuristic phụ là khoảng cách nhỏ nhất từ một box tới một goal trên floor graph.
4. Khi tìm được trạng thái làm tăng `score_me - score_other`, trả **hành động đầu tiên** của kế hoạch.
5. Mỗi lượt tính lại từ snapshot thật.
6. Hết thời gian hoặc node limit thì `Wait`.

Đây là chính sách tìm kiếm có giới hạn, **không phải minimax và không bảo đảm thắng trước một đối thủ tối ưu**. Điều này cần nói rõ trong vấn đáp/báo cáo.

Chạy hai agent:

```powershell
python main.py --mode compete --map maps/competitive/arena.txt --rounds 8 --agent-two agent-two --match-output results/match_agent2.json
```

## 5. Kết quả kiểm tra đã chạy trong môi trường thực hiện

- `python -m unittest discover -s tests -v`: **75 tests pass**.
- `two_boxes.txt`: UCS và A* đều tìm được cost **8**.
- Một lần benchmark 3 repeats trên môi trường Linux/Python 3.13.5: A* mở rộng **76** trạng thái, UCS **284**; cả hai đều cost 8. Đây chỉ là số liệu của map thử nghiệm này, không phải kết luận độ phức tạp tổng quát.
- Kiểm chứng `two_boxes.txt`, mẫu 50 trạng thái: **44** trạng thái có exact cost từ UCS, **143** cạnh được kiểm tra, **0** vi phạm admissibility và **0** vi phạm consistency; 6 trạng thái bị bỏ vì UCS chứng minh unsolvable. Đây là kiểm chứng thực nghiệm trên mẫu, không phải chứng minh toàn bộ không gian Sokoban.
- Demo `arena.txt`, 8 rounds, AgentOne vs AgentTwo: cả hai worker trả quyết định hợp lệ trong giới hạn; trận thử kết thúc hòa trên map này. Không dùng một trận đơn để đánh giá chất lượng agent.

## 6. Lưu ý quan trọng trước khi nộp

PDF đề chính thức ghi tại trang 4 rằng **việc sử dụng công cụ AI bị cấm** và source code có nội dung AI-generated có thể bị 0 điểm cho task tương ứng. Vì vậy nhóm phải tự đọc, hiểu, tự chỉnh sửa/viết lại theo quy định của môn và chịu trách nhiệm về tính xác thực của source code trước khi nộp; không nên nộp nguyên file này như sản phẩm do sinh viên tự viết.
