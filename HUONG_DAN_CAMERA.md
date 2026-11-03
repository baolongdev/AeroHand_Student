# Điều khiển Aero Hand bằng camera (OpenCV + MediaPipe)

Cập nhật: **03/11/2026**. Chương trình: `examples/dieu_khien_camera.py`, chạy nhanh bằng `ChayCamera.bat`.

Webcam đọc góc khớp ngón tay **trái** của người dùng, quy đổi sang góc khớp của Aero Hand tay trái và gửi lệnh vị trí qua SDK. Mặc định chương trình **chưa gửi lệnh**. Phải bấm SPACE và đặt tay khớp với vị trí robot thì robot mới bám theo.

## 1. Cài đặt (một lần, cần Internet)

`CaiDat.bat` **không** cài thư viện camera vì các thư viện này không có trong `wheels/` offline. Sau khi chạy `CaiDat.bat`, mở PowerShell tại thư mục gói:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-camera.txt
```

Đã kiểm tra với: Python 3.10.5 x64, `mediapipe==0.10.14`, `opencv-contrib-python 4.11.0.86` (cài kèm mediapipe) và `numpy 1.26.4`. Phải dùng numpy < 2 vì mediapipe 0.10.14 được biên dịch với numpy 1.x. Các bản mediapipe mới hơn có thể đã bỏ API `mp.solutions.hands` mà chương trình dùng.

## 2. Chạy

Đóng GUI, Serial Monitor và các script khác trước, vì mỗi lúc chỉ một chương trình được giữ cổng COM.

| Lệnh | Ý nghĩa |
|---|---|
| `ChayCamera.bat` | Tự tìm cổng Aero Hand (chip Espressif, USB VID `303A`) rồi nối. Chưa gửi lệnh |
| `ChayCamera.bat COM7` | Chỉ định cổng |
| `ChayCamera.bat none` | Chỉ xem camera, **không** mở COM |

Tùy chọn khi chạy bằng Python (`.venv\Scripts\python.exe examples\dieu_khien_camera.py ...`):

| Tùy chọn | Mặc định | Ý nghĩa |
|---|---|---|
| `--port` | `auto` | `auto`, `COMx` hoặc `none` |
| `--camera` | `0` | Số thứ tự webcam; thử `1` nếu máy có nhiều camera |
| `--hand` | `left` | Tay người dùng để điều khiển; chỉ nhận đúng tay này |
| `--thumb` | tắt | Điều khiển cả 3 kênh ngón cái. Mặc định ngón cái bị **khóa** |
| `--smooth` | `0.35` | Bộ lọc 0..1, giá trị nhỏ thì mượt hơn nhưng trễ hơn |
| `--max-speed` | `150` | Tốc độ tối đa gửi tới robot (độ/giây) |
| `--ignore-temp` | tắt | Không chặn khi servo nóng (vẫn hiện nhiệt độ). **Tự chịu rủi ro** |

## 3. Phím điều khiển

Phải bấm chuột vào cửa sổ camera để chọn nó thì phím mới có tác dụng.

| Phím | Chức năng |
|---|---|
| `O` | Lưu tư thế **mở**: xòe thẳng các ngón, ngón cái dang ra |
| `F` | Lưu tư thế **nắm**: nắm chặt, ngón cái gập qua lòng bàn tay về phía ngón út |
| `SPACE` | Bắt đầu đồng bộ, rồi tự chuyển sang điều khiển. Bấm lại để dừng |
| `R` | Xóa hiệu chỉnh, về giá trị mặc định |
| `Q` / `ESC` / nút ✕ | Thoát |

## 4. Quy trình sử dụng

1. Kiểm tra nhiệt độ servo: `.\.venv\Scripts\python.exe examples\tim_cong.py`.
2. Chạy `ChayCamera.bat` và đưa **tay trái** vào khung hình.
3. **Hiệu chỉnh:** bấm `O` khi tay mở và `F` khi tay nắm. Kết quả lưu vào `examples/hieu_chinh_camera.json` và tự nạp ở lần chạy sau. Hiệu chỉnh lại khi đổi người dùng, đổi vị trí camera, hoặc khi chương trình báo "Chua hieu chinh".
4. Bấm `SPACE`. Tiêu đề đổi thành **DAT TAY KHOP VACH TRANG**. Vạch trắng là vị trí thật của robot.
5. Chỉnh ngón tay cho thanh màu chạm vạch trắng. Khi mọi khớp đang được điều khiển đều lệch **≤ 10°** và giữ được **0,5 giây**, tiêu đề đổi thành **DANG DIEU KHIEN** và robot bắt đầu bám theo tay. Cách này giúp robot không bị giật lúc bắt đầu.
6. Cử động **chậm**, luôn sẵn sàng ngắt 6 V.
7. Bấm `Q` để thoát.

## 5. Đọc màn hình

- **Góc trái:** tên khớp, góc mục tiêu (độ) và thanh 0 → giới hạn khớp.
- **Màu thanh** thể hiện sai lệch giữa tay trên camera và **vị trí thật** của robot, đọc khoảng 10 lần/giây:

| Màu | Sai lệch |
|---|---|
| Xanh lá | ≤ 10° |
| Vàng | khoảng 25° |
| Đỏ | ≥ 40° |

- Số `eNN` bên phải mỗi thanh là sai lệch tính bằng độ. Khi chạy với `none` (không nối robot), thanh luôn màu xanh và không có vạch trắng.
- Kênh bị khóa (ngón cái khi không dùng `--thumb`) hiện màu xám với chữ **KHOA**.
- `Temp max` là nhiệt độ servo cao nhất, chuyển màu đỏ khi ≥ 45 °C.
- Dòng *KHONG THAY TAY LEFT* hiện khi camera không thấy tay trái. Tay phải trong khung hình bị bỏ qua.

## 6. Quy đổi tay người sang robot

| Kênh robot | Đo từ camera | Phạm vi robot |
|---|---|---|
| `thumb_abd` (ID 0) | Góc giữa xương bàn ngón cái và xương bàn ngón trỏ | 5–100° |
| `thumb_flex` (ID 1) | Khoảng cách đầu ngón cái → gốc ngón út, chia cho kích thước lòng bàn tay | 0–55° |
| `thumb_tip` (ID 2) | Tổng độ gập 2 khớp ngón cái | 0–90° |
| `index`…`pinky` (ID 3–6) | Tổng độ gập 3 khớp mỗi ngón | 0–90° |

Mỗi kênh được quy đổi tuyến tính theo hai tư thế đã lưu: mở = 0°, nắm = giới hạn khớp. 4 ngón bám khá sát. **Ngón cái chỉ gần đúng**, vì ngón cái người và ngón cái robot cấu tạo khác nhau.

`thumb_abd` có góc tối thiểu **5°** (`ROBOT_MIN` trong code). Lý do: trên bàn tay của lớp, ép kênh này về 0° làm servo ghì vào điểm chặn cơ khí; xem mục 8.

## 7. Cơ chế an toàn

- Khi mới nối, chương trình chưa gửi lệnh. Phải bấm SPACE và đồng bộ xong thì robot mới cử động.
- Tốc độ lệnh bị giới hạn (`--max-speed`), có bộ lọc chống rung.
- Mất tay khỏi khung hình quá 0,5 giây thì robot **giữ nguyên tư thế**.
- Chương trình đọc nhiệt độ mỗi 2 giây. Nếu có servo ≥ **45 °C**, nó dừng điều khiển và không cho bật lại (trừ khi chạy với `--ignore-temp`).
- **Khi thoát:** chỉ khi đã điều khiển robot trong lần chạy đó, các kênh đang được điều khiển mới từ từ về HOME (60°/s): 4 ngón về 0°, `thumb_abd` về 5°. Kênh bị khóa giữ nguyên. Nếu chỉ mở để xem, robot không cử động khi thoát.
- Đóng chương trình chỉ đóng cổng COM, **không tắt lực servo**. Muốn thả lực phải ngắt 6 V.

## 8. Ghi nhận khi thử trên bàn tay của lớp (03/11/2026)

- Lệnh vị trí bám chính xác: gửi 4 ngón 20° thì đo được 19,7–20,0°, gửi 40° thì đo được 39,1–39,4°.
- **`thumb_abd` ghì vào điểm chặn ở 0°.** Sau khi dùng ZERO_ALL trong GUI, kênh này có dòng khoảng 1900 đơn vị khi đứng yên và nóng tới 60 °C. Giữ ở khoảng 5° thì dòng còn khoảng 60 và servo nguội dần. **Không dùng ZERO_ALL để nghỉ tay.**
- **Ngón giữa (ID 4) tải cao bất thường:** ở 20° dòng khoảng 470, trong khi các ngón khác khoảng 50–80. Đây cũng là servo nóng nhất (57–68 °C). Cần tắt 6 V và kiểm tra dây gân, ma sát hoặc kẹt của ngón giữa.
- Mỗi lần mở cổng COM, ESP32 khởi động lại và in `[BOOT]...`. SDK có thể in `Invalid response ... got 91` ở lần đọc đầu; chương trình tự thử lại. Đây là reset không mất nguồn nên firmware **không** chạy Homing.
- Dòng `Timeout while reading actuations. Got 0 bytes.` thỉnh thoảng xuất hiện là do SDK chỉ chờ 10 ms. Chương trình giữ giá trị lần trước, không ảnh hưởng tới điều khiển.
- Giá trị dòng điện chỉ dùng để so sánh tương đối; hệ số quy đổi ra mA trong SDK chưa được xác nhận.

## 9. Xử lý lỗi

| Hiện tượng | Cách xử lý |
|---|---|
| Bấm SPACE không có tác dụng, báo *Servo con nong* | Servo ≥ 45 °C. Ngắt 6 V cho nguội, kiểm tra nguyên nhân ghì lực ở mục 8 |
| Kẹt ở *DAT TAY KHOP VACH TRANG* | Một khớp đang lệch > 10° (thanh vàng/đỏ). Chỉnh ngón đó chạm vạch trắng; nếu ngón cái khó khớp, chạy không có `--thumb` |
| *Khong tim thay Aero Hand* | Đóng GUI; kiểm tra cáp USB; có thể robot đang Homing sau khi cấp nguồn, đợi xong rồi chạy lại |
| *Khong mo duoc camera* | Thử `--camera 1`; đóng ứng dụng khác đang dùng webcam |
| Nhiệt độ hiện 0 °C | Đã ngắt 6 V. ESP32 vẫn trả lời qua USB nhưng servo không có dữ liệu |
| Kênh chạy ngược hoặc không nhạy | Hiệu chỉnh lại `O`/`F` cẩn thận; nếu vẫn sai, chỉnh hàm `raw_features` |
| `ModuleNotFoundError: mediapipe` | Chưa cài mục 1 |

## 10. Các file liên quan

| File | Nội dung |
|---|---|
| `examples/dieu_khien_camera.py` | Chương trình điều khiển bằng camera |
| `examples/tim_cong.py` | Tự tìm cổng Aero Hand; chạy riêng để in góc khớp và nhiệt độ (chỉ đọc) |
| `examples/dieu_khien_co_ban.py` | Ví dụ SDK: đọc trạng thái; với `--move` thì gập nhẹ 4 ngón 30° rồi mở lại |
| `examples/hieu_chinh_camera.json` | Hiệu chỉnh cá nhân, tự tạo khi bấm O/F. Không phát kèm gói |
| `ChayCamera.bat` | Chạy nhanh chương trình camera |
| `requirements-camera.txt` | Thư viện camera cài thêm |
