# BÁO CÁO GIỮA KỲ — INTRODUCTION TO ARTIFICIAL INTELLIGENCE

**Đề tài: Sokoban — tìm kiếm một tác tử và cạnh tranh hai tác tử**

> Đây là mẫu nội dung tiếng Việt để nhóm hoàn thiện thành file báo cáo theo định dạng giảng viên yêu cầu. Chưa phải báo cáo kết quả hoàn chỉnh. Chỗ [BỔ SUNG] cần thay bằng nội dung/số liệu thật. Không nộp nguyên khung này.

Mã học phần: 503043  
Mã nhóm: [BỔ SUNG]  
Giảng viên: [BỔ SUNG]  
Hạn nộp: 17:00 ngày 05/10/2026 (giờ Việt Nam)

| MSSV | Họ tên | Email | Công việc | Hoàn thành thực tế |
|---|---|---|---|---|
| 524H0091 | Phạm Minh Huy | [BỔ SUNG] | Lõi, UCS, engine và AgentOne | [ĐIỀN SAU KIỂM TRA] |
| 524H0026 | Lưu Minh Phương | [BỔ SUNG] | A*, heuristic, kiểm chứng, AgentTwo | [ĐIỀN SAU KIỂM TRA] |
| 524H0087 | Phan Hồng Đăng | [BỔ SUNG] | GUI, benchmark, đóng gói | [ĐIỀN SAU KIỂM TRA] |

## 1. Mục tiêu và phạm vi

[Mô tả hai chế độ, đầu vào/đầu ra, yêu cầu thực nghiệm, công nghệ và các giới hạn. Phân biệt yêu cầu của đề với quy ước nhóm trong DECISIONS.md.]

## 2. Mô hình bài toán một tác tử — Huy

### 2.1 Không gian trạng thái
[Mô tả thành phần cố định và thành phần thay đổi; khóa trạng thái và ý nghĩa thùng không phân biệt.]

### 2.2 Trạng thái đầu, hành động, chuyển trạng thái và điều kiện đích
[Nêu xử lý C, ô trống, vùng ngoài, đi và đẩy; minh họa một chuyển trạng thái.]

### 2.3 Chi phí
[Quy ước cost=1 cho mỗi hành động hợp lệ; giải thích vì sao số hành động bằng tổng cost trong bản này.]

## 3. UCS và A* — Huy, Phương

### 3.1 UCS
[Giả mã, hàng đợi ưu tiên, g, best_g, phát hiện trạng thái cũ, tái dựng đường đi, điều kiện dừng.]

### 3.2 A*
[Giả mã, f=g+h, heuristic sử dụng, cập nhật đường tốt hơn, giới hạn tài nguyên.]

### 3.3 Đặc điểm và hạn chế
[Giải thích điều kiện đầy đủ/tối ưu tương ứng với chi phí, heuristic và cách cài; không khẳng định chung nếu chưa đủ điều kiện.]

## 4. Heuristic và kiểm chứng — Phương

### 4.1 Định nghĩa
[Công thức, trực giác, chi phí tính, tiền xử lý, không dùng Manhattan/Euclidean.]

### 4.2 Admissibility và consistency
[Lập luận h(s) ≤ h*(s), h(s) ≤ c(s,a,s')+h(s'), h(goal)=0; lưu ý các trường hợp không có nghiệm.]

### 4.3 Thực nghiệm
[Nguồn h*, cách sinh/lấy mẫu trạng thái và cạnh, phạm vi bao phủ, cách xử lý timeout.]

| Map | Trạng thái kiểm tra | Cạnh kiểm tra | Vi phạm admissibility | Vi phạm consistency | Ghi chú phạm vi |
|---|---:|---:|---:|---:|---|
| [DỮ LIỆU THẬT] | | | | | |

[Kết luận thực nghiệm trong phạm vi kiểm tra, phân biệt với chứng minh tổng quát.]

## 5. So sánh hiệu năng — Đăng, Huy và Phương xác nhận

[Máy, OS, Python, pygame; bộ map; số lần lặp; đo thời gian và bộ nhớ thế nào; có tính tiền xử lý; giới hạn; điều kiện dùng chung.]

| Map | Thuật toán | Trạng thái kết quả | Số hành động/cost | Thời gian (ms) | Expanded | Peak memory (đơn vị rõ) |
|---|---|---|---:|---:|---:|---:|
| [DỮ LIỆU THẬT] | | | | | | |

[Biểu đồ nếu có; bàn luận trade-off; timeout phải ghi rõ. Không kết luận độ phức tạp tổng quát chỉ từ vài map.]

## 6. Cạnh tranh hai tác tử — Huy, Phương

### 6.1 Mô hình và luật
[Định nghĩa n, joint action, xung đột, owner, điểm, cướp thùng, hòa, timeout. Minh họa hai ý định trên cùng snapshot.]

### 6.2 Thuật toán điều khiển
[Mỗi agent dùng thuật toán nào đã học, mục tiêu, heuristic nếu có, tái lập kế hoạch, giới hạn tìm kiếm và fallback.]

### 6.3 Giao diện và thời gian
[Hai file agent, giao diện thay thế, runner thực thi deadline, hành vi lỗi, log thời gian thực tế.]

| Trận/map | n | Agent 1 | Agent 2 | Điểm cuối | Timeout mỗi bên | Đã đổi bên kiểm tra? |
|---|---:|---|---|---|---|---|
| [DỮ LIỆU THẬT] | | | | | | |

## 7. GUI và kiến trúc OOP — Đăng

[Các lớp chính, phụ thuộc giữa core/search/UI/competition; ảnh thật của hai chế độ; hướng dẫn Space/→/←; nhập n; owner màu; đảm bảo replay không làm tính lại agent.]

## 8. Kiểm thử và tương thích — Cả nhóm

| Nhóm kiểm tra | Kết quả thực tế | Bằng chứng | Hạn chế |
|---|---|---|---|
| Parser/lõi | [BỔ SUNG] | | |
| UCS/A* và lời giải | [BỔ SUNG] | | |
| Heuristic | [BỔ SUNG] | | |
| Đồng thời/owner/timeout | [BỔ SUNG] | | |
| Windows | [BỔ SUNG] | | |
| macOS 13.7.8 Intel | CHƯA KIỂM TRA, cập nhật khi có bằng chứng | | |

## 9. Mức độ hoàn thành và hạn chế

| Yêu cầu đề | Sản phẩm/bằng chứng | Phần còn thiếu | Tỷ lệ hoàn thành thực tế |
|---|---|---|---|
| 1. Mô hình một tác tử | | | |
| 2. UCS/A* và heuristic | | | |
| 3. Thời gian/không gian | | | |
| 4. Kiểm chứng heuristic | | | |
| 5. GUI/OOP/môi trường | | | |
| 6. Mô hình cạnh tranh | | | |
| 7. Bộ điều khiển ≤1000 ms | | | |
| 8. GUI cạnh tranh/file agent | | | |
| Task 2. Trình bày | | | |

## 10. Tài liệu và nguồn hỗ trợ

[Slide môn học, nguồn code mẫu được phép, tài liệu thư viện, hỗ trợ đã sử dụng theo hướng dẫn giảng viên. Nêu phần nhóm tự sửa/kiểm tra và kết quả thực tế; không che giấu nguồn hoặc chép kết luận không hiểu.]

## Phụ lục: chạy lại và vấn đáp

[Lệnh cài/chạy, map đã dùng, đường dẫn CSV/log, mô tả tái lập kết quả.]

Câu hỏi cả ba cần tự trả lời:

1. Vì sao vị trí người chơi là một phần của trạng thái?
2. Vì sao C phải lưu cả đích lẫn thùng?
3. UCS tối ưu theo đại lượng nào? Khi cost=1, liên hệ với BFS thế nào?
4. Vì sao A* cần h và khi nào bảo đảm tối ưu?
5. Admissibility khác consistency thế nào? Thực nghiệm có phải chứng minh không?
6. Vì sao hai agent phải quan sát cùng trạng thái trước lượt?
7. Nếu agent không bao giờ trả về thì runner xử lý thế nào?
8. Bộ nhớ đang đo gồm gì? Thời gian có tính tiền xử lý không?
9. Vì sao lùi replay không phải hành động kéo thùng?
10. Những yêu cầu nào chưa được kiểm chứng trên máy thật?
