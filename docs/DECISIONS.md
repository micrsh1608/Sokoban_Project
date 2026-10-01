# Quy ước thiết kế v0.1 — do nhóm lựa chọn

Các mục sau cụ thể hóa những chỗ đề chưa quy định chi tiết. Đây không phải trích nguyên luật của giảng viên. Khi có hướng dẫn bổ sung, sửa tài liệu và kiểm thử cùng lúc.

## Một tác tử

- Tọa độ `(row, column)`. Không đổi sang `(x, y)` trong solver; GUI tự chuyển.
- Trạng thái: vị trí tác tử + frozenset vị trí thùng. Tường/đích cố định trong Board.
- Số thùng bằng số đích; tất cả thùng nằm trên đích thì thắng.
- Mỗi hành động đi hoặc đẩy hợp lệ tốn 1; hành động đẩy đã bao gồm bước người tiến vào ô thùng cũ, không cộng thêm.
- Không sinh hành động lỗi hoặc Wait trong tìm kiếm một tác tử.
- Output: hướng đầy đủ North/East/West/South và tổng chi phí. Chi phí bằng số hành động với quy ước này.
- Giữ ô đích khi người/thùng đi khỏi. Không kéo, không đẩy chuỗi nhiều thùng.
- Ngoài vùng tường bao là VOID, không coi padding là nền.

## Cạnh tranh: quy ước triển khai

1. Map dùng A và P, hai vị trí khác nhau. Chủ sở hữu thùng là 0/1/None.
2. Một bước là một lượt đồng thời của cả hai. Chạy đúng n lượt; không dừng chỉ vì mọi đích đã có thùng.
3. Hai tác tử nhận cùng snapshot trước lượt. Không để bên thứ hai nhìn kết quả bên thứ nhất rồi mới chọn.
4. Có Wait. Hành động không hợp lệ chuyển thành đứng yên; vẫn tính lượt.
5. Mỗi ý định gồm tập vị trí vật thể bị di chuyển và vị trí đích của chúng: đi thường di chuyển một người, đẩy di chuyển người và một thùng.
6. Quy tắc bảo thủ để dễ giải thích: không được đi/đẩy vào vị trí tác tử khác trong snapshot đầu lượt, dù tác tử đó định rời đi. Không được đẩy thùng vào vị trí thùng khác trong snapshot đầu lượt.
7. Nếu cả hai ý định hợp lệ cùng tác động một thùng hoặc có vị trí đích của vật thể trùng nhau, hủy cả hai ý định. Nếu chỉ một ý định không hợp lệ riêng lẻ, ý định hợp lệ còn lại vẫn chạy nếu không xâm phạm vật thể đứng yên.
8. Quy tắc 6 cấm đổi chỗ trực tiếp, đi theo vào ô vừa được giải phóng trong cùng lượt, và đi xuyên nhau. Tính đồng thời là chọn trên cùng snapshot và commit chung; không có ưu tiên cố định cho người 1.
9. Thùng khi được đẩy đến đích thuộc tác tử thực hiện lần đẩy đó. Khi rời đích, owner=None. Thùng không di chuyển giữ owner. Thùng C ban đầu trung lập, không tính điểm cho ai.
10. Điểm hiện tại là số thùng đang trên đích có owner của tác tử; không cộng dồn lịch sử. Có thể cướp điểm bằng cách đẩy thùng đối thủ ra rồi đặt lại.
11. Sau lượt n, so điểm; bằng nhau là hòa. n phải là số nguyên dương.
12. Mỗi tác tử được tối đa 1000 ms cho một lần quyết định; timeout/lỗi/đầu ra không hợp lệ thành Wait và ghi log. Đây là cách nhóm diễn giải giới hạn, không phải khẳng định đề nói rõ theo từng agent.
13. Mỗi agent ở một file riêng, dùng Observation giống nhau. Không sửa engine từ agent.
14. Replay trận đấu phải khôi phục vị trí, owner, điểm và lượt. Quay lại để xem không gọi lại agent.

## Timeout và công bằng

- Runner cần worker process riêng; dùng cơ chế spawn hoạt động trên Windows và macOS, có main guard.
- Khởi tạo worker trước trận; mỗi yêu cầu kèm round ID để không nhận nhầm kết quả cũ sau timeout.
- Worker đo thời gian tính bằng perf_counter và kiểm tra budget; runner cũng thực thi deadline từ lúc gửi yêu cầu, không chỉ đo sau khi hàm đã trả.
- Nếu worker quá hạn, kết quả lượt đó bị loại; xử lý worker treo trước lượt sau. Không tích lũy vô hạn các thread không dừng.
- Ghi cả thời gian quyết định và overhead để giải thích khi vấn đáp. Bắt đầu budget đủ thận trọng dưới 1000 ms.
- Đảo vị trí khởi đầu/agent trên cùng map khi đánh giá công bằng.

## Nội dung không được coi là đã có

Engine đã thực thi chuyển trạng thái đồng thời, va chạm, quyền sở hữu, điểm và kết thúc. Các quy định về thuật toán tác tử, runner cưỡng chế timeout 1000 ms và GUI/replay cạnh tranh vẫn cần triển khai. Không ghi yêu cầu 7–8 đã hoàn thành chỉ vì engine hoạt động. Xem COMPETITIVE_RULES_GUIDE.md để cài và kiểm tra bản cập nhật luật.
