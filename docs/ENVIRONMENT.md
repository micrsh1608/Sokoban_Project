# Môi trường và tính tương thích

## Mục tiêu

- Máy phát triển của ba người: Windows (theo thông tin nhóm).
- Môi trường đích trong đề: macOS 13.7.8 Ventura, Intel Core i5.
- Đề xuất chung: Python 3.11 64-bit + pygame==2.6.1, chỉ thêm thư viện khi cần.
- requirements.txt chốt pygame; các module khác của khung dùng thư viện chuẩn Python.

Nguồn đã tra cứu ngày 01/10/2026: https://pypi.org/project/pygame/2.6.1/ có wheel CPython 3.11 cho Windows x86-64 và macOS x86-64. Đây là bằng chứng có gói phân phối phù hợp kiến trúc, KHÔNG phải bằng chứng ứng dụng đã chạy trên Mac Intel Ventura. Chưa xác nhận trực tiếp Windows/Mac cho bản khung này.

## Cách chạy trên Mac khi mượn được máy

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python main.py
```

Không chép thư mục .venv từ Windows sang Mac. Tạo lại môi trường. Đường dẫn dùng pathlib, tài nguyên nằm trong dự án, không dùng đường dẫn D:\\... cố định. Không phụ thuộc font hệ thống; GUI dùng font mặc định pygame.

## Việc nhóm phải kiểm tra trực tiếp

1. Windows: mở GUI, bàn phím, chọn map, gọi solver, đóng khi đang tìm kiếm.
2. Mac Intel: cài từ đầu, các thao tác trên; cần bằng chứng OS/CPU/Python/pygame thật.
3. Sau khi thêm runner: spawn worker, timeout, đóng chương trình, không còn process con treo.
4. Ghi cấu hình bằng `python -m platform`, `python --version`, `python -m pip show pygame` và thông tin máy tương ứng.
5. Nếu chưa mượn được Mac: ghi rõ chưa kiểm chứng, liên hệ giảng viên/nhờ kiểm tra sớm. Windows/Linux pass không thay thế kiểm tra Mac.
