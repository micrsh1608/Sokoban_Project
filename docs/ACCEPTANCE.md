# Checklist trước nộp — đánh dấu bằng chứng, không đánh dấu dựa trên tên file

## Chức năng và thuật toán

- [ ] Mô tả đầy đủ state/actions/transition/goal/cost.
- [ ] Nhập đường dẫn map, đọc đúng %, A, B, D, C, dấu cách.
- [ ] UCS và A* dùng chung luật, trả actions và total cost.
- [ ] Phát lại lời giải xác minh trạng thái cuối; map đã giải trả 0 hành động.
- [ ] Phân biệt unsolvable với timeout/limit.
- [ ] Heuristic không Manhattan/Euclidean, có lập luận hai thuộc tính.
- [ ] Kiểm chứng có dữ liệu thật, số state/edge và phạm vi rõ.
- [ ] Benchmark cả thời gian lẫn bộ nhớ với phương pháp thống nhất.
- [ ] pygame OOP, chọn UCS/A*, hiển thị số hành động.
- [ ] Space/→/← hoạt động đúng.
- [ ] Hai agent quyết định từ cùng snapshot, cập nhật đồng thời.
- [ ] Không đi xuyên nhau; test tranh ô, đổi chỗ, cùng đẩy thùng, va chạm đích người/thùng.
- [ ] Thùng đổi owner/điểm đúng; C ban đầu xử lý nhất quán.
- [ ] Nhập n; kết thúc đúng n; hòa được xử lý.
- [ ] Hai file bộ điều khiển riêng; chạy ≤1000 ms theo quy ước; lỗi/timeout có log.
- [ ] GUI cạnh tranh có màu thùng, điểm/lượt và lịch sử đầy đủ.
- [ ] Chạy trên Windows máy khác; có bằng chứng Mac Intel Ventura hoặc ghi rõ hạn chế.

## Tài liệu và trình bày

- [ ] Báo cáo những gì thực sự đã làm, theo yêu cầu bổ sung của giảng viên.
- [ ] Chốt định dạng báo cáo (Word/PDF), giới hạn trang/mẫu nếu có.
- [ ] Slide PDF 4:3, nền sáng, in xám vẫn rõ, không dán mã nguồn thô.
- [ ] Họ tên/MSSV/email, phân công và tỷ lệ hoàn thành thành viên/từng task.
- [ ] Phương pháp, giả mã/sơ đồ, kết quả, ưu nhược điểm.
- [ ] Thuyết trình ≤5 phút; chuẩn bị vấn đáp tiếng Việt cho cả ba.
- [ ] Video ≤3 phút; demo.txt chứa URL thật, mở được với người chấm.
- [ ] Không còn số liệu giả, placeholder hoặc tuyên bố chưa kiểm chứng.

## Đóng gói

- [ ] Mã nhóm thật đã bổ sung.
- [ ] Mỗi thành viên có folder `AI_midterm_<group_ID>_<MSSV>` tương ứng.
- [ ] Có source (chia task vào thư mục con), presentation.pdf, demo.txt.
- [ ] Có báo cáo bổ sung; README chỉ rõ vị trí và lệnh chạy.
- [ ] Map/tài nguyên/requirements cần thiết đã được đưa vào.
- [ ] Không đóng gói .venv, __pycache__, dữ liệu riêng tư, link demo chưa điền.
- [ ] Giải nén sang thư mục mới và chạy lại thành công.
- [ ] Cả ba tự nộp trước 17:00 ngày 05/10/2026; mục tiêu nội bộ 15:00.
