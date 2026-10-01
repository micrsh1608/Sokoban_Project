# Đối chiếu với slide môn học đã nhận

Đã đối chiếu nội dung AI-lec04-UninformedSearch.pdf và AI-lec05-InformedSearch.pdf ngày 01/10/2026. Hai tài liệu chứa lý thuyết/giả mã; chưa có hai file mã Python UCS/A* mà nhóm nói có sẵn.

| Tài liệu / trang PDF | Nội dung áp dụng | Vị trí liên quan |
|---|---|---|
| lec04 trang 10–11 | UCS chọn g thấp nhất, frontier ưu tiên, kiểm tra đích khi lấy ra | search/ucs.py; INTEGRATION.md |
| lec04 trang 14 | Điều kiện đầy đủ/tối ưu, chi phí tối thiểu dương | Báo cáo mục 3; quy ước cost=1 |
| lec05 trang 13 | A* dùng f=g+h | search/astar.py |
| lec05 trang 17–18 | A* không tự động tối ưu với mọi heuristic | Báo cáo mục 3/4 |
| lec05 trang 19–20 | Admissibility, tree search và tính tối ưu | Bộ kiểm chứng; báo cáo mục 4 |
| lec05 trang 21–22 | Consistency, graph search và điều kiện tối ưu | Heuristic, xử lý đường đi tốt hơn |

## Những chỗ không nên chuyển từ slide sang code một cách máy móc

1. Điều kiện “not in explored or frontier” của giả mã UCS trang 11 được hiểu là trạng thái chưa có trong cả explored lẫn frontier; không dịch thành biểu thức Python `not in explored or not in frontier` vì sẽ sai logic. Có thể quản lý bằng best_g và bỏ heap entry cũ thay cho thao tác decrease-key, nhưng phải giải thích cách tương đương.
2. Slide lec05 trang 19 liệt kê Manhattan/Euclidean làm ví dụ lý thuyết; đề dự án vẫn CẤM hai khoảng cách này. Yêu cầu đề tài quyết định heuristic được sử dụng.
3. Slide lec05 trang 21 nói admissibility chưa đủ cho graph search trong cách đóng trạng thái mà không mở lại. Khung yêu cầu xử lý đường có g tốt hơn; nếu dùng reopen, cần nói rõ khác biệt và điều kiện bảo đảm. Dù vậy dự án vẫn yêu cầu thảo luận/kiểm chứng consistency.
4. Điều kiện h(goal)=0 cần nêu rõ khi dùng consistency để suy ra admissibility trên trạng thái có đường đến đích.
5. Cost=1 làm UCS tương đương BFS về thứ tự theo chi phí/tầng (khác tie-break có thể chọn lời giải khác cùng cost). Vẫn phải cài UCS theo đề, không chỉ đổi tên BFS.

Không chép số liệu/mô hình minh họa đồ thị của slide thành số liệu thực nghiệm Sokoban. Kết quả phải sinh từ bản đồ và chương trình của nhóm.
