# Thay đổi so với source gốc

- GUI khởi động/kết nối ở trạng thái không gửi vị trí; thêm Start/Pause Position Commands.
- Homing, Set ID, Calibrate Mid, đổi chế độ torque và lỗi ghi serial không tự bật lại luồng vị trí.
- Icon được đặt trong package và sửa đường dẫn để tìm được khi giải nén/cài SDK.
- HandConfig.h trong source firmware tham khảo chọn LEFT_HAND; file.bin vẫn là bản v0.2.0_lefthand gốc, không sửa.
- Hướng dẫn/checklist tiếng Việt, bộ cài local, ví dụ chỉ đọc, wheel offline và manifest được thêm cho lớp.
- Không đặt sẵn cổng COM bắt buộc và không cài sẵn mốc home/đóng/mở cá nhân vào bộ điều khiển.
- Không thay hệ số quy đổi dòng hay sửa GET_ALL trong SDK; hướng dẫn đã ghi giới hạn của hai phần này.

## Bổ sung 03/11/2026 (sau khi phát gói)

- Thêm `examples/tim_cong.py` (tự tìm cổng, chỉ đọc), `examples/dieu_khien_co_ban.py` (ví dụ SDK) và `examples/dieu_khien_camera.py` (điều khiển bằng webcam với OpenCV + MediaPipe), `ChayCamera.bat`, `requirements-camera.txt`, `HUONG_DAN_CAMERA.md/.html`.
- Bổ sung vào README và Hướng dẫn vận hành: bảng quy đổi slider, lỗi `GET_POS NoneType`, cảnh báo ZERO_ALL làm thumb_abd ghì vào điểm chặn, ghi nhận ngón giữa tải cao, nhiệt độ 0 °C khi tắt 6 V, cách cài lại `.venv` đúng Python 3.10.
- Không sửa SDK, GUI, firmware hay file `.bin`. Thư viện camera không nằm trong `wheels/` offline và lock; cần Internet để cài.
- `examples/hieu_chinh_camera.json` là hiệu chỉnh cá nhân, không phát kèm gói.
- `SHA256SUMS.txt` được tạo lại cho các file đã thay đổi và file mới.
