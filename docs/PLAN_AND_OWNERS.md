# Phân công và tiến độ đến 17:00 ngày 05/10/2026

## Phương án được chọn

Một ứng dụng Python/pygame OOP, không web/database, không tách service. Dùng chung luật và hợp đồng dữ liệu. Có một đầu mối chịu trách nhiệm mỗi module, nhưng mỗi người phải hiểu luồng toàn hệ thống để vấn đáp.

Mức 8 giờ/người/tuần là thời lượng nhóm cung cấp, KHÔNG có nghĩa còn chắc chắn 24 giờ công trước hạn. Nhóm cần tự xác nhận có dành được khoảng 8 giờ/người từ 01–05/10 hay không. Bảng dưới là ngân sách khởi đầu rất chặt, không phải cam kết hoàn thành toàn bộ. Nếu code mẫu khó ghép hoặc phần cạnh tranh gặp lỗi, cần thêm thời gian; không lấy thời gian kiểm chứng/báo cáo để che thiếu chức năng.

## Huy — 524H0091_Phạm Minh Huy

| Việc | File chính | Dự trù giờ | Tiêu chí bàn giao |
|---|---|---:|---|
| Đọc/kiểm tra lõi, chốt spec | core/*; DECISIONS.md | 0.75 | Giải thích trạng thái, bước đẩy, C và cost |
| Ghép UCS mẫu | search/ucs.py | 1.5 | Tiny/two_boxes, solved/unsolvable/timeout đúng |
| Joint engine + AgentOne | competitive/engine.py; agent_one.py; runner.py cùng Đăng | 3.5 | Cập nhật đồng thời, owner, va chạm, agent có quyết định |
| Tích hợp, viết báo cáo phần mình, vấn đáp | tests; mục 2/3/6 của báo cáo | 2.25 | Giải thích và demo phần mình; kiểm tra chéo A* |

Huy phụ trách yêu cầu 1, phần UCS yêu cầu 2, mô hình cạnh tranh yêu cầu 6, một phần yêu cầu 7. Khối engine có rủi ro cao nhất; nếu quá thời lượng phải báo sớm để cả nhóm điều chỉnh.

## Phương — 524H0026_Lưu Minh Phương

| Việc | File chính | Dự trù giờ | Tiêu chí bàn giao |
|---|---|---:|---|
| Ghép A* mẫu | search/astar.py | 1.5 | Đường đi đúng; cost bằng UCS trên mẫu nhỏ |
| Heuristic, lập luận, dữ liệu và kiểm chứng | search/heuristics.py; experiments/verify_heuristic.py | 3 | Kết quả thật, số trạng thái/cạnh, phạm vi rõ |
| AgentTwo | competitive/agent_two.py | 1.5 | Dùng tìm kiếm, cùng protocol, quyết định trong budget |
| Báo cáo, kiểm tra chéo, vấn đáp | mục 3/4/6 của báo cáo | 2 | Giải thích admissibility, consistency, deadline |

Phương phụ trách phần A* yêu cầu 2, yêu cầu 4, một phần yêu cầu 7. Hai agent có thể dùng ý tưởng tìm kiếm chung nếu giải thích được; đề không ghi bắt buộc phải là hai thuật toán khác nhau. Hai file phải độc lập theo giao diện chung, không nhập logic của nhau khiến việc thay một agent bị lỗi.

## Đăng — 524H0087_Phan Hồng Đăng

| Việc | File chính | Dự trù giờ | Tiêu chí bàn giao |
|---|---|---:|---|
| Hoàn thiện GUI một/hai tác tử | ui/*; competitive/runner.py cùng Huy | 3 | Nhập n, màu owner, điểm, pause/forward/back |
| Benchmark và tổng hợp | experiments/benchmark.py; results | 1.5 | Có thời gian, bộ nhớ, limits, môi trường và số liệu thật |
| Ghép báo cáo, slide, video | docs/REPORT_TEMPLATE.md; submission | 2 | Nội dung do cả ba cung cấp; định dạng đúng |
| Cài máy sạch, kiểm tra bàn giao | docs/ENVIRONMENT.md; ACCEPTANCE.md | 1.5 | Windows test, kế hoạch Mac, kiểm tra ZIP/link |

Đăng chủ trì yêu cầu 3, 5, 8 và ghép sản phẩm Task 2. Không phải tự viết toàn bộ nội dung nghiên cứu của hai người còn lại.

## Lịch cụ thể, giờ Việt Nam

| Ngày | Mốc phải đạt |
|---|---|
| 01/10 | Cả ba chạy khung; gửi code UCS/A*; đọc contracts; chốt quy ước và chia file; liên hệ mượn máy Mac/nhờ kiểm tra |
| 02/10 | UCS/A* giải map nhỏ; GUI phát lời giải; bắt đầu kiểm chứng và engine đồng thời |
| 03/10 | Trận cạnh tranh chạy được với hai agent; phát hiện timeout; có benchmark và kiểm chứng ban đầu |
| 04/10 | Dừng thêm tính năng; sửa lỗi; hoàn thiện báo cáo, slide 4:3 và video ≤3 phút; diễn tập vấn đáp |
| 05/10 trước 12:00 | Kiểm tra trên máy khác, rà kết quả, kiểm tra đúng tên và file nộp |
| 05/10 trước 15:00 | Mục tiêu nội bộ: cả ba nộp và giữ xác nhận; 2 giờ dự phòng so với hạn 17:00 |

## Quy tắc làm việc

- Nếu có Git: nhánh `huy-core-ucs`, `phuong-astar-heuristic`, `dang-ui-experiments`. Chỉ push/merge khi nhóm đã tạo repo và thống nhất; khung chưa kết nối repo nào.
- `core/model.py`, `search/contracts.py`, `competitive/contracts.py` là giao diện chung: đổi phải thông báo cả nhóm.
- Mỗi ngày trao đổi ngắn: đã chạy được gì, kẹt gì, file nào sắp đổi. Dùng bằng chứng chạy được thay cho phần trăm cảm tính.
- Mỗi người ghi nguồn, thử nghiệm, lỗi đã sửa và hạn chế vào phần báo cáo mình.
- Khi thiếu giờ: bỏ trang trí, âm thanh, editor map và tính năng ngoài đề; vẫn giữ checklist các mục bắt buộc. Báo trung thực phần chưa hoàn thành.
- Không cần tốn thời gian tạo asset hình: khung dùng hình học pygame, dễ chạy đa nền tảng.
