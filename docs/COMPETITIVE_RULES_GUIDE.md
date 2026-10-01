# Luật cạnh tranh hai tác tử — cập nhật ngày 01/10/2026

## Phạm vi

Đã triển khai CompetitionEngine: xác thực trạng thái, xây ý định từ cùng snapshot, xử lý xung đột, commit đồng thời, owner, điểm, tăng lượt, kết thúc và thắng/hòa. Đây là cách nhóm cụ thể hóa các chỗ đề chưa quy định; không phải giao thức chính thức do giảng viên cung cấp.

Chưa triển khai: AgentOne/AgentTwo tự tìm kiếm, runner cưỡng chế 1000 ms, GUI cạnh tranh. `main.py --mode compete` vẫn báo runner chưa triển khai. Demo trong gói dùng hành động định sẵn, KHÔNG phải hai AI thi đấu. Timeout phải do runner xử lý thành Wait và ghi log; engine không tự đo thời gian tác tử.

## Cài đặt vào khung có sẵn

Giải nén Sokoban_Competitive_Rules_Update.zip vào thư mục tạm, ghép các file theo đường dẫn vào Sokoban_Starter:

| Tệp | Việc |
|---|---|
| source/task1/sokoban/competitive/engine.py | Thay engine cũ |
| tests/test_core.py | Cập nhật bài test cũ vốn mong đợi engine chưa triển khai |
| tests/test_competitive.py | Thêm 27 bài test cạnh tranh |
| demo_competition_rules.py | Thêm ở cùng cấp main.py |
| maps/competitive/steal_demo.txt | Thêm map cho demo |
| docs/DECISIONS.md | Cập nhật tình trạng luật đã triển khai |
| docs/COMPETITIVE_RULES_GUIDE.md | Hướng dẫn này |

Không sửa contracts.py, UCS, A*, GUI hoặc runner. Nếu đã tự thay test_core.py, chỉ cần sửa test_competition_initialization_only: bỏ assertRaises(NotImplementedError), gọi step với hai Wait rồi kiểm tra round_index=1 và players giữ nguyên. File test_core trong gói là phiên bản của khung gốc đã sửa đoạn này.

## Chạy trên Windows của Huy

```powershell
cd "D:\TDTU\Introduction AI\Sokoban_Starter"
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_competitive.py" -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe demo_competition_rules.py
```

Mong đợi: 27 test riêng thành công; tổng 48 nếu có 12 test lõi và 9 test UCS của bản trước. Nếu thiếu test_ucs.py thì tổng là 39, chưa có kiểm thử UCS trong lượt chạy đó.

Demo in 8 lượt, điểm các lượt 1–2=(1,0), lượt 3–7=(0,0), lượt 8=(0,1), Winner: Agent 2, Replay snapshots: 9. Snapshot 0 là trạng thái đầu.

## Các quy tắc cụ thể

- Actor index/owner: 0 là người thứ nhất (A); 1 là người thứ hai (P); None là trung lập. Box.id giữ nguyên khi đẩy.
- n là số nguyên dương, không nhận float/bool. Một joint step tăng đúng một lượt kể cả cả hai đứng yên/bị chặn.
- Đi vào tường/vùng ngoài/người kia thì không di chuyển. Đẩy chỉ một thùng; không đẩy vào tường, thùng khác hoặc người kia.
- Các vị trí bị chiếm trong snapshot đầu vẫn chặn hành động, dù chủ thể đó định rời đi. Do đó cấm đổi chỗ trực tiếp và theo vào ô người kia vừa rời trong cùng lượt.
- Hai ý định hợp lệ cùng tác động một thùng hoặc có đích đến vật thể trùng nhau: hủy cả hai, không ưu tiên bên nào.
- Đích đến bao gồm cả người và thùng: bắt được va chạm người-người, thùng-thùng, thùng-người.
- Một bên tự không hợp lệ không làm bên độc lập còn lại mất lượt.
- Đẩy thùng đến đích: owner là tác tử đẩy. Đẩy khỏi đích: owner=None. Thùng không di chuyển giữ owner. C ban đầu trung lập.
- Đẩy trực tiếp từ đích này sang đích khác: quyền sở hữu theo người thực hiện lần đẩy mới. Không cộng dồn điểm theo số lần đặt.
- Điểm được tính từ số thùng đang trên đích thuộc tác tử, không lưu một biến điểm cộng dồn dễ sai.
- Chạy đủ n lượt; không kết thúc sớm khi mọi thùng trên đích. Hết n lượt: so điểm, bằng nhau hòa. Gọi bước tiếp sau kết thúc bị từ chối.
- Hành động cá nhân sai như None hoặc chuỗi lạ thành Wait, reason=invalid_action. Thiếu/thừa số lượng hành động là lỗi tích hợp và bị ValueError.
- Trạng thái hỏng (trùng người/thùng, ngoài nền, owner sai, thiếu/đổi ID, lượt sai) bị từ chối.

## API giao cho Phương và Đăng

`engine.initial`: trạng thái đầu bất biến.

`engine.step(state, (action0, action1))`: trả CompetitionState mới; giữ chữ ký khung ban đầu.

`engine.resolve(state, (action0, action1))`: trả TurnResult với state, actions, moved và reasons. actions là yêu cầu đã chuẩn hóa, KHÔNG có nghĩa hành động đó được thực hiện; xem moved/reasons.

`engine.scores(state)`: tuple điểm `(điểm A, điểm P)`.

`engine.finished(state)`: kiểm tra đủ n lượt.

`engine.winner(state)`: chỉ gọi khi kết thúc; trả 0 hoặc 1, trả None nếu hòa. Không dùng None để biểu diễn trận còn đang chạy; gọi sớm bị ValueError.

Phương dùng step để mô phỏng trạng thái, không tự viết một bộ luật khác. Đăng dùng resolve để hiển thị lý do đứng yên và log; lưu đầy đủ state mỗi lượt để tua lại, không chạy lại agent khi xem lịch sử. Quyền owner quyết định màu thùng trong GUI tương lai.

## Luồng cài đặt và cách giải thích

1. validate_state: giữ các bất biến của bàn cờ.
2. _intent: tính mục tiêu người/thùng của từng bên từ cùng state.
3. So sánh hai intent: cùng box_id hoặc giao nhau giữa các đích đến thì hủy.
4. Tạo danh sách vị trí và thùng mới từ những intent còn hợp lệ.
5. Tạo CompetitionState mới với round_index+1; trạng thái đầu không bị sửa.

Vòng for commit không biến game thành tuần tự: cả hai intent đã được tính và giải quyết xung đột trước đó; không bên nào được quan sát trạng thái trung gian. Đây là điểm quan trọng để giải thích tính đồng thời.

## Bằng chứng kiểm tra

Đã chạy trên Linux/Python 3.12.14. Chưa chứng nhận máy Windows Python 3.13 hoặc macOS Intel; nhóm cần chạy các lệnh trên máy mình.

27 test cạnh tranh gồm các trường hợp đi độc lập, chờ, tường, tranh ô, đổi chỗ, đi theo, đẩy/owner, C trung lập, đích sang đích, chặn thùng/người, cùng thùng, hai thùng cùng ô, thùng và người cùng ô, ghi điểm đồng thời, dữ liệu lỗi, kết thúc/thắng/hòa, và cướp điểm qua 8 lượt.

Một test trong số đó kiểm tra 1000 cặp hành động (40 bố trí lấy mẫu có seed cố định × 25 joint actions) và chạy lại khi đổi danh tính hai người; trạng thái/owner/lý do đối xứng và bất biến được giữ. Đây là mẫu kiểm thử hữu hạn, không phải chứng minh cho mọi bản đồ.

Tổng với lõi và UCS: 48 test thành công. Demo 8 lượt cũng đã chạy thành công qua parser và engine thật.

## Nội dung báo cáo của Huy

Cập nhật mục 6.1: trạng thái gồm hai người, thùng có ID/owner, lượt hiện tại, n; joint action; quy tắc va chạm; điểm; kết thúc. Thêm bảng một vài test và demo cướp điểm. Trình bày rõ các quy ước nhóm tự chọn (cấm đi theo vào ô vừa rời, cách tính điểm hiện tại, C trung lập).

Phần tiếp theo: AgentOne và runner, trong đó phải bảo đảm hai agent thấy cùng snapshot và có cơ chế giới hạn 1000 ms thực sự. Không ghi toàn bộ chế độ cạnh tranh hoặc yêu cầu 7–8 đã hoàn thành ở mốc engine này.
