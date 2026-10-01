# AgentOne và bộ chạy trận — Huy — 01/10/2026

## Trạng thái bản cập nhật

Đã triển khai AgentOne dùng BFS có giới hạn, runner hai worker process độc lập dùng spawn, deadline mỗi quyết định, callback tích hợp GUI, CLI compete và xuất log JSON. Gói này cần khung dự án và bản cập nhật engine cạnh tranh trước đó.

Chưa sửa phần AgentTwo của Phương, A*, heuristic hoặc GUI cạnh tranh của Đăng. Mặc định đối thủ là WaitAgent, chỉ để kiểm tra. Thắng đối thủ đứng yên không chứng minh chất lượng cạnh tranh với một AI khác. Các dòng trong tài liệu cũ ghi AgentOne/runner chưa triển khai được thay thế bởi tài liệu này.

## Cài đặt

Ghép file trong ZIP vào đúng vị trí tương đối trong Sokoban_Starter:

- Thay source/task1/sokoban/competitive/agent_one.py và runner.py.
- Thêm source/task1/sokoban/competitive/baseline_agent.py.
- Thay source/task1/sokoban/cli.py để có các tùy chọn chạy trận.
- Thêm tests/test_agent_one.py, tests/test_runner.py, tests/runner_fixtures.py.
- Thêm docs/AGENT_ONE_RUNNER_GUIDE.md và docs/HANDOFF_AGENT_RUNNER.md.
- evidence/agent_one_arena_8_rounds.json là kết quả thật của lần kiểm tra Linux, không phải kết quả trên máy nhóm.

Nếu cli.py đã được Đăng chỉnh, ghép riêng các thay đổi của nhánh mode compete và hai tùy chọn --agent-two/--match-output thay vì ghi đè mất công việc. Không thay agent_two.py.

Không thêm thư viện: toàn bộ tính năng mới dùng thư viện chuẩn Python. Dùng .venv Python 3.13 hiện có của bạn, không tạo lại. Không chạy riêng agent_one.py hoặc runner.py; khởi chạy qua main.py (đã có main guard để spawn).

## Lệnh chạy Windows

```powershell
cd "D:\TDTU\Introduction AI\Sokoban_Starter"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py --mode compete --map maps/competitive/arena.txt --rounds 8 --agent-two wait --match-output results/match_huy.json
```

Nếu đã đủ các bản trước: 62 tests. Riêng kiểm tra mới là 7 test AgentOne + 7 test runner. Kết quả demo 8 lượt đã kiểm tra: lượt 1–3 AgentOne đi East, lượt 3 đạt điểm 1–0, hết lượt 8 thắng 1–0. Agent 2 là WAIT BASELINE, chương trình ghi rõ. Những lượt còn lại không đủ kế hoạch tăng điểm trong phạm vi xét nên agent có thể Wait.

CLI này chạy trong Terminal; chưa mở GUI hai tác tử. --rounds là n. Kết thúc đúng n dù đã có thùng trên đích. Log có thể bị ghi đè nếu dùng lại cùng --match-output; đặt tên khác khi cần giữ nhiều lần chạy.

Sau khi Phương hoàn thành AgentTwo:

```powershell
.\.venv\Scripts\python.exe main.py --mode compete --map maps/competitive/arena.txt --rounds 30 --agent-two agent-two --match-output results/match_two_agents.json
```

Nếu AgentTwo vẫn là stub: status=error, detail trong JSON có NotImplementedError và lượt đó thành Wait. Điều này là xử lý lỗi, không phải đã tích hợp thành công AgentTwo.

## AgentOne hoạt động như thế nào?

1. Nhận Observation gồm board, trạng thái trước lượt, agent_id.
2. Đánh giá lợi thế hiện tại: điểm mình trừ điểm đối phương.
3. BFS duyệt các chuỗi hành động hợp lệ thông qua CompetitionEngine.resolve, mô phỏng đối thủ đứng yên.
4. Khi tìm trạng thái tăng lợi thế, trả hành động ĐẦU TIÊN của đường đi đến đó.
5. Lượt sau quan sát trạng thái thật và tìm lại. Không thực hiện nguyên kế hoạch cũ khi đối thủ đã thay đổi bàn cờ.
6. Chỉ duyệt đến số lượt còn lại của trận; mặc định tối đa 5000 trạng thái mở rộng mỗi quyết định.
7. Hết budget hoặc không tìm được kế hoạch tăng lợi thế: trả Wait.

Có thể tăng lợi thế bằng đưa thùng lên đích hoặc đẩy thùng đối phương ra ngoài. Không dùng Manhattan/Euclidean. Không phải minimax, không dự đoán hành động đối phương, không đảm bảo thắng hay tìm được kế hoạch trên map lớn. BFS này tìm cải thiện gần trong mô hình đối phương Wait; không tối ưu điểm cuối trận toàn cục. Có thể đứng yên nếu kế hoạch nằm ngoài thời gian/số node/lượt còn lại hoặc đối thủ chặn đường. Đây là bản điều khiển cơ bản dễ giải thích và kiểm tra; muốn tăng sức mạnh phải đo thêm trên nhiều map/đối thủ.

last_stats trong worker chứa expanded, reason, đôi khi plan_steps để debug trực tiếp. Hiện các số này không được truyền vào log trận; không báo chúng như metrics đã xuất. Log trận có thời gian quyết định.

## Runner và giới hạn 1000 ms

- Hai worker process độc lập, khởi tạo sẵn trước lượt đầu bằng multiprocessing spawn; giữ controller giữa các lượt bình thường.
- Khởi tạo/restart worker có giới hạn chờ 5 giây, nằm ngoài ngân sách tính quyết định. Worker không khởi tạo được sẽ dừng trận với lỗi rõ ràng.
- Gửi cùng snapshot before đến cả hai worker, chỉ khác agent_id. Gửi cả hai trước khi chờ kết quả.
- Mỗi bên có deadline 1000 ms mặc định, tính từ lúc runner bắt đầu gửi yêu cầu. Worker nhận budget hợp tác 85% (850 ms) để chừa khoảng truyền dữ liệu/lập lịch.
- Runner chờ hai kết nối cùng lúc. Không chờ hết 1000 ms cho người 1 rồi cấp thêm 1000 ms cho người 2.
- Kết quả nhận sau deadline bị loại, kể cả agent nói đã tính xong trước đó. Timeout trở thành Wait.
- Worker treo bị terminate/kill và được tạo mới trước lượt sau. Không giữ vô hạn thread không dừng; trạng thái nội bộ agent sẽ mất khi restart.
- Mỗi request/response có round ID; sai ID bị từ chối.
- Exception/đầu ra sai cũng thành Wait và ghi lý do. Lỗi khởi tạo module/class là lỗi cấu hình, không bị che thành một trận thành công.
- Chỉ commit engine sau khi cả hai quyết định đã được giải quyết. Sau đó gọi callback.
- Dọn worker trong finally khi kết thúc, lỗi hoặc callback phát sinh exception.

Không khẳng định hệ điều hành bảo đảm dừng chính xác ở 1000.000 ms: elapsed_ms khi phát hiện timeout có thể nhỉnh hơn do lập lịch; thời gian dọn/restart là ngoài quyết định. Quy tắc được thực thi là KHÔNG chấp nhận phản hồi muộn, với cơ chế process riêng để ngắt controller treo. Đây không phải sandbox bảo mật để chạy mã độc.

## Log JSON

- controllers: đường dẫn module:class của hai bộ điều khiển; baseline được nhận diện rõ.
- board: width/height, walls/floors/goals.
- initial: snapshot ban đầu.
- turns: before, after, decisions, reasons, scores của từng lượt.
- decisions: action, status (ok/timeout/error/invalid_action), elapsed_ms ở runner, compute_ms do worker đo khi có kết quả, detail lỗi.
- scores, winner: kết quả cuối; winner=0/1 là index tác tử, null là hòa.
- decision_ms: ngân sách yêu cầu.

Status ok nghĩa hàm trả về hợp lệ trong hạn, không có nghĩa hành động nhất định di chuyển được. Xem reasons của engine để biết tường/va chạm. Một hành động hợp lệ có thể bị hủy do đối thủ.

## Kết quả kiểm tra thực tế

Linux/Python 3.12.14: 62 test pass. Chưa kiểm chứng trực tiếp Windows 3.13 hoặc Mac Intel.

7 test AgentOne: kế hoạch tăng điểm, tái lập kế hoạch đạt đích, agent_id=1, deadline đã hết, giới hạn node, giới hạn lượt còn lại, trận đã kết thúc.

7 test runner: AgentOne ghi điểm + lưu/đọc JSON + phát lại đúng, cùng snapshot đầu, validation budget, callback lỗi vẫn cleanup, exception/invalid action thành Wait, agent treo bị ngắt và restart qua hai lượt, lỗi constructor không để sót worker. Kiểm tra active_children sau mỗi test runner không thấy tiến trình con mới còn sống. Test treo dùng budget 150 ms để chạy nhanh; đường chạy CLI thật dùng budget 1000 ms.

CLI thật: arena 8 lượt thắng baseline 1–0; log trong evidence. Kiểm tra thêm chọn AgentTwo stub: lỗi được ghi nhận và chuyển thành Wait đúng như thiết kế.

## Việc của Huy còn lại để nghiệm thu

1. Chạy tests và trận demo trên Windows của mình.
2. Đọc và giải thích BFS, mô hình đối thủ Wait, chặn quá hạn bằng worker, cùng snapshot và hậu quả restart.
3. Gửi contracts + engine + tài liệu handoff cho Phương/Đăng (nhóm tự gửi, bản cập nhật không tự gửi tin nhắn).
4. Khi có AgentTwo thật: chạy nhiều map, đổi bên, kiểm tra điểm/timeout/va chạm; không dùng kết quả baseline để kết luận cân bằng.
5. Viết phần báo cáo AgentOne/runner bằng kết quả thật, ghi hạn chế và trạng thái kiểm chứng Mac.
