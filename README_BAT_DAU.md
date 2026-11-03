# Bộ Aero Hand tay trái cho sinh viên

Bản phát hành: **03/11/2026**, Windows 64-bit.

## Bắt đầu trong 5 bước

1. **Giải nén toàn bộ ZIP**, không mở/chạy file trực tiếp bên trong ZIP. Có thể giải nén thành `C:\AeroHand_Student` hoặc thư mục khác.
2. Cần có **Python >=3.10, 64-bit, có Tcl/Tk**. Python không được kèm trong ZIP. Xem [Python trên Windows](https://docs.python.org/3/using/windows.html). Không dùng bản embeddable thiếu Tk/pip cho GUI này.
3. Chạy **CaiDat.bat** một lần. Chương trình tạo `.venv` riêng, cài thư viện rồi cài SDK từ source trong gói. Không cần cắm bàn tay để cài đặt.
4. Chạy **KiemTraCaiDat.bat** nếu muốn kiểm tra; công cụ này không mở COM hay gửi lệnh servo.
5. Đọc **HUONG_DAN_SU_DUNG_AERO_HAND.md**, rồi mở **ChayGUI.bat**. Chọn đúng COM (máy lớp đã dùng COM11; ESP32-S3 hiện tên *USB Serial Device*, USB VID `303A`), Baud921600, Rate50Hz. GUI bắt đầu với **position streaming OFF**; kéo slider chỉ có tác dụng sau khi bấm **Start Position Commands**.

Gói wheel offline được tạo và kiểm tra bằng **CPython3.10 Windows x64**. Nếu Python khác không dùng được wheel offline, CaiDat sẽ tải thư viện phù hợp từ PyPI; cần Internet. Có thể bắt buộc cài offline bằng `powershell -NoProfile -ExecutionPolicy Bypass -File .\CaiDat.ps1 -OfflineOnly`.

Nếu chuyển thư mục sau khi đã cài, nên giải nén lại vào thư mục đích rồi chạy CaiDat tại đó. Không sao chép `.venv` từ máy khác.

## Sơ đồ ID của bàn tay lớp

| ID | Cơ cấu |
|---|---|
|0|Tay đòn cứng, dạng/khép ngang ngón cái|
|1|Dây gập khớp gốc/phần dưới ngón cái|
|2|Dây cuộn phần đầu ngón cái|
|3|Ngón trỏ|
|4|Ngón giữa|
|5|Ngón áp út|
|6|Ngón út|

ID1/2 đã được đảo đúng và xác nhận ngày02/11. Hiệu chỉnh hành trình ngón cái sau thay đổi này chưa được tài liệu xác nhận hoàn tất; giảng viên cần kiểm tra trước khi cho chạy hết biên.

## Trước khi cho bàn tay chuyển động

- Firmware chuẩn v0.2.0 có thể **tự Homing khi ESP32 khởi động/sụt áp**, dù GUI chưa Connect. Chuẩn bị dây/cơ khí và khoảng trống trước khi cấp điện.
- Nút **Start Position Commands** sẽ gửi tất cả mục tiêu slider đang đặt. Kiểm tra đủ bảy slider trước khi bật.
- **Pause/Disconnect không tắt lực**. Ngắt nguồn6V để ngắt động lực; tắt6V trước khi tháo giắc/chỉnh dây.
- Homing/Set to Open Position có thể chuyển động cả khi streaming đang Pause. Chỉ thao tác khi đã được hướng dẫn.
- **ZERO_ALL** đưa mọi khớp về 0°. Trên tay lớp, thumb_abd (ID0) ở 0° bị ghì vào điểm chặn, servo nóng dần khi đứng yên. Không dùng ZERO_ALL làm tư thế nghỉ; kiểm tra nhiệt độ sau khi dùng.
- Không dùng Set ID hoặc đổi ID để thử vận hành; bảy ID của tay lớp đã được đặt.

## Trong gói có gì?

- Hướng dẫn vận hành và checklist tiếng Việt.
- `aero-hand-open/sdk`: GUI đã chỉnh và Python SDK, cài từ source local.
- `aero-hand-open/firmware/main/bin/firmware_v0.2.0_lefthand.bin`: ứng dụng tay trái; GUI nạp tại0x10000. Chỉ nạp khi có yêu cầu, không cần nạp lại mỗi buổi học.
- `aero-hand-open/firmware/main`: source tham khảo, HandConfig chọn LEFT_HAND. Source có thể chứa tính năng mới hơn file.bin; không mặc định biên dịch ra đúng binary phát hành.
- `aero-hand-open/hardware/Gen1_OPEN_Assembly_Guide.pdf`: tài liệu lắp ráp gốc.
- `examples/doc_trang_thai.py`: ví dụ chỉ đọc; `tools/kiem_tra_cai_dat.py`: kiểm tra cài đặt.
- `examples/tim_cong.py`: tự tìm cổng Aero Hand, in góc khớp và nhiệt độ (chỉ đọc).
- `examples/dieu_khien_co_ban.py`: ví dụ SDK đọc trạng thái; với `--move` gập nhẹ 4 ngón rồi mở lại.
- `examples/dieu_khien_camera.py`, `ChayCamera.bat`, `requirements-camera.txt`: điều khiển bằng camera, xem **HUONG_DAN_CAMERA.md**.
- `wheels` và requirements: thư viện cài đặt. `SHA256SUMS.txt`: kiểm tra tính toàn vẹn các file trong gói.

Không đưa môi trường máy giảng viên, log thử nghiệm, mốc hiệu chỉnh cá nhân hoặc công cụ chẩn đoán/đảo ID/tìm chặn vào bộ dùng thường ngày này.

## Ví dụ đọc dữ liệu

Đóng GUI để nhường COM, mở PowerShell tại thư mục giải nén:

```powershell
.\.venv\Scripts\python.exe examples\doc_trang_thai.py --port COM11
```

Script không gửi Homing/vị trí/lực. Với firmware chuẩn, đủ7 servo có nguồn mới có bộ dữ liệu nhóm đáng tin; dữ liệu0/cũ không chứng minh servo thật đang ở vị trí0.

Không cần biết số COM:

```powershell
.\.venv\Scripts\python.exe examples\tim_cong.py
```

Script tìm cổng có chip Espressif, xác nhận bằng lệnh đọc GET_POS rồi in góc khớp và nhiệt độ ID0–6. Nhiệt độ toàn0°C nghĩa là đã ngắt6V.

## Điều khiển bằng camera

Webcam đọc ngón tay trái của người dùng và điều khiển bàn tay theo. Cài thêm thư viện (cần Internet) rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-camera.txt
.\ChayCamera.bat
```

Chương trình tự tìm COM và chưa gửi lệnh cho tới khi bấm SPACE và đặt tay khớp với robot. Đọc **HUONG_DAN_CAMERA.md** trước khi dùng.

## Ghi chú cài đặt

- Chỉ dùng một GUI/script/Serial Monitor giữ cổng COM cùng lúc.
- `CaiDat.ps1` chỉ dùng thư mục gói và `.venv`, không yêu cầu admin, không đổi ExecutionPolicy toàn máy.
- Nếu cài offline báo thiếu wheel phù hợp, dùng Internet hoặc nhờ giảng viên chuẩn bị wheel theo đúng phiên bản Python/kiến trúc máy.
- Bộ này đã kiểm tra bằng Python3.10 x64; Python khác cần kiểm tra lại cài đặt, không được khẳng định đã thử phần cứng.
- Nếu `.venv` lỡ tạo bằng Python khác (ví dụ 3.12), CaiDat sẽ tải thư viện từ PyPI và phiên bản có thể lệch lock. Cài Python3.10 x64, xóa `.venv`, rồi chạy `powershell -NoProfile -ExecutionPolicy Bypass -File .\CaiDat.ps1 -PythonExe "<đường dẫn python3.10>" -OfflineOnly`.
- `requirements-camera.txt` cài thêm mediapipe/OpenCV/numpy vào `.venv`, ngoài lock offline. Chạy lại CaiDat không gỡ các gói này.

## Nguồn và giấy phép

Aero Hand Open: Chestnut Robotics/TetherIA. [Repository](https://github.com/chestnut-robotics/aero-hand-open), [tài liệu](https://docs.tetheria.ai/docs/intro/).
Mã SDK/firmware giữ LICENSE/NOTICE Apache2.0; tài liệu phần cứng đi kèm LICENSE CC BY-NC-SA4.0 trong thư mục hardware. Thư viện bên thứ ba giữ metadata/giấy phép trong wheel.
Xem **THAY_DOI_TRONG_GOI.md** để biết các chỉnh sửa local.
