# Bàn giao AgentOne/runner cho Phương và Đăng

## Phương: AgentTwo

Giữ file competitive/agent_two.py và class AgentTwo. Constructor không cần tham số bắt buộc. Phải có choose_action(observation, deadline) trả Action. deadline là mốc perf_counter tuyệt đối bên trong worker; không dùng time.time so với deadline này. Kiểm tra thời gian trong vòng lặp. Không gọi pygame, input(), hoặc sửa trạng thái dùng chung. Bộ điều khiển có thể giữ bộ nhớ giữa lượt bình thường nhưng phải hoạt động được sau restart do timeout/error.

Observation.state là CompetitionState trước lượt, observation.board là Board, observation.agent_id là 0 hoặc 1. Không hardcode AgentTwo luôn index 1 nếu muốn đổi bên đánh giá. Các Box.id giữ nguyên sau di chuyển; owner=None/0/1. Mô phỏng bằng engine và giữ đúng luật nhóm.

Runner nhận tên module:class nên có thể đổi hai agent_specs ở API để đảo bên. CLI hiện cố định AgentOne ở bên 0; chọn --agent-two agent-two để dùng file Phương. Không nhập AgentOne thay cho phần Phương rồi báo đã hoàn thành hai bộ điều khiển độc lập.

## Đăng: GUI cạnh tranh

API chặn (blocking): run_match(engine, agent_specs=(AGENT_ONE, AGENT_TWO), decision_ms=1000, on_turn=callback).

Callback nhận TurnRecord sau mỗi lượt, cùng thread gọi run_match. Hãy chạy run_match trong thread điều phối riêng và đưa record qua queue.Queue để GUI main thread nhận; không gọi pygame display/event từ callback của thread nền. Vẫn giữ if __name__ == '__main__' ở entrypoint để multiprocessing spawn không chạy lặp toàn chương trình trên Windows/Mac.

TurnRecord.before/after là snapshot bất biến đầy đủ, có box owner và round index. Lưu initial + từng after để replay. Giao diện nên thể hiện controller đang dùng, n, lượt, điểm, màu owner và tình trạng timeout/error.

Space/→/← cho replay: dùng snapshot đã lưu; không gọi lại choose_action khi tua. Nếu muốn pause tính trận thật, cần thêm cơ chế pause/cancel của coordinator. Runner hiện không có API pause/cancel trực tiếp; callback có thể báo lỗi để thoát có cleanup nhưng đó không phải UI hủy trận hoàn chỉnh. Không để việc đóng cửa sổ bỏ thread điều phối chạy nền; cần bổ sung tín hiệu hủy trước khi ghép GUI cuối. API hiện phù hợp chạy trận headless hoặc tính trận trước rồi phát lại.

Giới hạn 1000 ms áp dụng quyết định; thời gian vẽ, setup worker và dọn process không nằm trong compute_ms. Log elapsed_ms là thời gian roundtrip runner quan sát, compute_ms là thời gian worker tính. Không dùng chúng thay thời gian tìm kiếm UCS/A* một tác tử trong benchmark.

## Các tình huống cần kiểm tra sau tích hợp

- Hai agent thật ra quyết định từ cùng snapshot và nhận đúng agent_id.
- Hai bên chọn hành động hợp lệ nhưng xung đột: engine hủy đúng, GUI không tự di chuyển trước kết quả.
- Thùng đổi owner khi ra/vào đích; điểm và màu thay đổi cùng snapshot.
- Worker timeout/error: dòng trạng thái rõ, Wait, trận vẫn đủ n lượt.
- Replay không đổi điểm do gọi lại agent; JSON phát lại trùng trạng thái đã ghi.
- Đóng GUI khi trận đang chạy không để sót worker/coordinator; cần triển khai quản lý hủy như lưu ý trên.
