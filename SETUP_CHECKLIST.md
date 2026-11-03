# Aero Hand Open — checklist setup (sau khi lắp cơ khí)

> Cập nhật 03/11/2026: xem hướng dẫn vận hành đầy đủ tại [HUONG_DAN_SU_DUNG_AERO_HAND.md](HUONG_DAN_SU_DUNG_AERO_HAND.md). GUI trong dự án mặc định **không gửi vị trí khi Connect**; cần bấm **Start Position Commands** để bật slider. Pause/Disconnect không tắt lực servo.

Môi trường: `C:\AeroHand_Student\.venv` (Python 3.10, SDK cài từ source `aero-hand-open/sdk`, esptool 5.6).
Mở GUI: chạy `ChayGUI.bat`.
Firmware đã xác nhận cho bàn tay này: `aero-hand-open/firmware/main/bin/firmware_v0.2.0_lefthand.bin` (tay trái).

## 1. Điện
- [ ] XIAO ESP32-S3 đã hàn header, cắm vào TTLinker Mini / PCB của hãng
- [ ] Nguồn servo **6 V DC, ≥10 A**, ổn áp (rail servo tách riêng khỏi USB 5 V)
- [ ] Đo cực tính trước khi cấp nguồn

## 2. Nạp firmware (chỉ cần USB, chưa cần nguồn 6 V)
- [ ] Cắm USB-C → Device Manager thấy COM mới (USB JTAG/serial debug unit)
- [ ] GUI → Refresh → chọn COM → **Upload Firmware** → chọn đúng tay (right/left)
- [ ] Chỉ dùng file .bin trong `main/bin` (ghi ở offset 0x10000), không dùng merged bin

## 3. Đặt ID servo (bỏ qua nếu servo đã được hãng đặt sẵn ID)
Mỗi lần chỉ cắm **1 servo** lên bus, cấp 6 V + USB → Connect → **Set ID**:

| ID | Kênh |
|---|---|
| 0 | Thumb abduction |
| 1 | Thumb flexion |
| 2 | Thumb tendon |
| 3 | Index |
| 4 | Middle |
| 5 | Ring |
| 6 | Pinky |

- Current limit giữ **1023**
- Chỉ coi đặt ID thành công khi ACK/readback xác nhận đúng ID; timeout hoặc mã lỗi cần kiểm tra nguồn và số servo trên bus
- Đã đặt đủ ID 0–6; không đặt/đảo lại khi sử dụng bình thường. ID 0 là tay đòn cứng, ID 1 kéo gốc ngón cái, ID 2 kéo đầu ngón cái
- Nếu thử slider, kiểm tra đủ cả bảy giá trị trước khi bật streaming; lệnh vị trí được gửi cho cả bàn tay

## 4. Homing
- Firmware có thể **tự Homing khi ESP32 khởi động/cấp nguồn/sụt áp**; GUI Pause không chặn quy trình này → chỉ khởi động khi dây/cơ khí sẵn sàng và có khoảng trống
- Hoặc bấm **Homing** trong GUI; chờ ACK (tối đa ~3 phút), lúc đó mọi lệnh khác bị bỏ qua
- Chuyển động lạ / dây chùng / dây tuột khỏi puly → tắt 6 V, sửa cơ khí trước, sau đó mới kiểm tra lại mốc; không gửi Homing lặp để chữa lỗi dây

## 5. Kiểm tra
- [ ] Chỉ bật **Start Position Commands** khi các mốc đã kiểm chứng; thử nhỏ từng bước, Rate 50 Hz. 0/1 là hai mốc phần mềm, không tự chứng minh đã đúng giới hạn cơ khí
- [ ] Ưu tiên GET_POS, GET_TEMP, GET_CURR riêng. GET_ALL hiện có hạn chế cách hiển thị POS; dòng raw và dòng SDK quy đổi không cùng thang số
- [ ] **Trim Servo** chỉ chỉnh mốc mở; thử từng bước nhỏ 1–5°. Không dùng để chữa đầu đóng hoặc dây luồn sai
- [ ] **Calibrate Mid** chỉ dùng khi đã xác nhận firmware hỗ trợ; thấy nút trên GUI không chứng minh file .bin hiện tại có lệnh này
- [ ] Servo giật mạnh, ép vào chặn, dây tuột hoặc nóng nhanh khi đứng yên → **cắt nguồn 6 V**, kiểm tra tải/cơ khí trước khi thử tiếp

## 6. Python
```python
from aero_open_sdk.aero_hand import AeroHand
hand = AeroHand(port="COMx")
```
Ví dụ trong `aero-hand-open/sdk/examples`: `run_sequence.py`, `power_grasp.py`, `get_info.py`, `trim_servo.py`...
