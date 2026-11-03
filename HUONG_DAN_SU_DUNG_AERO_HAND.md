> Bản phát cho sinh viên. `C:\AeroHand_Student` trong ví dụ là thư mục giải nén;
> có thể chọn thư mục khác. Các file BAT/PS1 tự tìm thư mục của chính gói.
> Hướng dẫn theo bàn tay trái của lớp; bàn tay khác cần kiểm tra ID và mốc riêng.

# Hướng dẫn sử dụng và điều khiển Aero Hand tay trái

Cập nhật: **03/11/2026**. Áp dụng theo cấu hình đã xác nhận gần nhất ngày 02/11/2026: bàn tay trái tại `C:\AeroHand_Student`, firmware **`firmware_v0.2.0_lefthand.bin`** và GUI cài từ source trong môi trường `.venv` của dự án.

## 1. Trạng thái hiện tại và sơ đồ servo

Đã đặt đủ bảy ID. Ngày 02/11/2026 đã đảo lại ID 1 và ID 2, đọc lại xác nhận, rồi khôi phục firmware tay trái v0.2.0 để dùng GUI.

| ID | Nhãn trên GUI | Cơ cấu thực tế |
|---|---|---|
| **0** | `thumb_abduction` | Tay đòn cứng: dạng/khép ngang cả ngón cái |
| **1** | `thumb_flex` | Dây cáp: gập khớp gốc/phần dưới ngón cái |
| **2** | `thumb_tendon` | Dây cáp: cuộn phần đầu ngón cái |
| **3** | `index_finger` | Ngón trỏ |
| **4** | `middle_finger` | Ngón giữa |
| **5** | `ring_finger` | Ngón áp út |
| **6** | `pinky_finger` | Ngón út |

**ID đúng chưa có nghĩa là hành trình đã đúng.** Sau lần đảo ID 1/2, cần kiểm tra lại dây và hiệu chỉnh ngón cái trước khi chạy toàn hành trình hoặc demo nắm tay. Tài liệu này không xác nhận rằng phần hiệu chỉnh đó đã hoàn tất.

Các mốc thử ID 3 từng lưu khi chạy firmware chẩn đoán là mốc tham chiếu của phiên thử, không phải một bộ hiệu chỉnh đã hoàn thiện cho firmware chuẩn. Không lấy các số encoder cũ làm lệnh chạy trực tiếp.

## 2. Chuẩn bị nguồn và cơ khí

- Dùng nguồn servo **6 V DC ổn áp**; cấu hình nguồn trong hướng dẫn phần cứng là **6 V, 10 A**. USB là đường giao tiếp và nguồn cho bộ điều khiển theo cách đi dây của board.
- Để công tắc/ngắt nguồn 6 V trong tầm với. Tắt 6 V trước khi tháo giắc servo, tháo puly, buộc hoặc chỉnh dây.
- Dây nằm đúng rãnh, không chéo hoặc kẹp vào khung; nút chặn không trượt. Dây điện không vướng tay đòn và puly.
- Kiểm tra lò xo hồi và dây liên động giữa các đốt. Không cố vặn trục servo qua lực cản.
- Dọn trống vùng ngón tay chuyển động trước khi cấp điện; không đặt tay người vào vùng khớp/puly.

### Chú ý khi khởi động

Firmware chuẩn có thể **tự Homing khi ESP32 khởi động do cấp nguồn hoặc sụt áp**. Việc GUI đang đóng, chưa Connect hay đã Pause không ngăn được Homing do firmware tự chạy.

- Nếu giữ USB liên tục và ESP32 đã khởi động xong: để GUI ở trạng thái dừng gửi vị trí trước khi cấp lại 6 V.
- Nếu khởi động lại cả bộ: chỉ làm khi cơ khí/dây đã sẵn sàng cho Homing. Chuẩn bị nguồn servo rồi cấp nguồn bộ điều khiển; với cách đi dây dùng USB nuôi ESP32, đó là cấp 6 V cho servo rồi cắm USB. Nếu board nuôi ESP32 từ 6 V, nó có thể khởi động ngay khi bật 6 V.
- Không bật nguồn servo giữa một quy trình Homing đã bắt đầu khi servo chưa có nguồn. Nếu không chắc trạng thái khởi động, dừng và xác định lại trước khi vận hành.
- Khi cần cấp điện nhưng tuyệt đối chưa được chuyển động để sửa cơ khí, không dựa vào nút Pause của GUI để thay cho firmware/chế độ thả trôi phù hợp.

## 3. Mở GUI và kết nối

1. Chạy **`C:\AeroHand_Student\ChayGUI.bat`**. File này dùng đúng Python/SDK trong `.venv` của dự án.
2. Bấm **Refresh**, chọn cổng của ESP32. Cổng đã dùng là **COM11**, nhưng có thể thay đổi nếu đổi cổng USB.
3. Chọn **Baud = 921600**, **Rate = 50 Hz**.
4. Bấm **Connect**. Đọc RX Log để xác nhận kết nối.
5. Trong bản GUI đã chỉnh tại dự án này, kết nối mới luôn có **position streaming OFF**. Chưa bấm **Start Position Commands** nếu chưa kiểm tra các slider và mốc cơ khí.

Nếu cần mở bằng PowerShell:

```powershell
Set-Location C:\AeroHand_Student
.\.venv\Scripts\python.exe -m aero_open_sdk
```

Chỉ một chương trình giữ cổng COM tại một thời điểm: GUI, Serial Monitor, script Python và công cụ nạp firmware không nên cùng mở COM11.

## 4. Các nút quan trọng

| Nút | Chức năng và điều cần nhớ |
|---|---|
| **Start Position Commands** | Bắt đầu gửi toàn bộ giá trị slider đang đặt; bàn tay có thể chuyển động ngay |
| **Pause Position Commands** | Ngừng gửi vị trí mới; **không tắt lực** đang giữ trong servo |
| **Disconnect** | Đóng cổng COM; **không phải lệnh thả trôi** |
| **Homing** | Chạy quy trình tìm mốc trên firmware, có chuyển động; chờ ACK hoàn tất |
| **Set to Open Position** | Gửi lệnh mở cho toàn bộ bàn tay ngay cả khi streaming đang Pause; không dùng làm nút dừng khẩn cấp |
| **Set Speed** | Đặt giới hạn tốc độ cho ID được chọn trong điều khiển vị trí; không dùng giá trị 0 để thay cho việc dừng/cắt nguồn |
| **Set Torque** | Đặt giới hạn lực cho ID được chọn trong điều khiển vị trí; khác với chế độ Torque Control |
| **Trim Servo** | Dịch mốc mở của kênh; không chỉnh độc lập mốc đóng |
| **GET_POS** | Đọc vị trí chuẩn hóa theo mốc hiệu chỉnh, không phải encoder raw |
| **GET_TEMP** | Đọc nhiệt độ theo thứ tự ID 0–6 |
| **GET_CURR** | Đọc dòng theo cách quy đổi của SDK; xem lưu ý ở mục 7 |
| **Set ID** | Công cụ GUI yêu cầu một servo trên bus; hiện đã đủ ID, không dùng lại trong vận hành bình thường |
| **Upload Firmware** | Nạp chương trình cho ESP32; không phải nút hiệu chỉnh hành trình |

**Pause chỉ chặn luồng vị trí liên tục.** Các nút có tác dụng chuyển động riêng như Homing, Set to Open Position hoặc Torque Control vẫn có thể gửi lệnh của chúng.

## 5. Homing và hiệu chỉnh sau khi sửa dây

### Khi nào cần kiểm tra lại mốc?

Sau khi dây tụt/thay dây, đổi nút buộc hoặc chiều quấn puly, tháo lắp tay đòn, đổi ID, hoặc khi vị trí mở/đóng không còn khớp thực tế.

### Quy trình Homing

1. Hoàn tất luồn và cố định dây; kiểm tra đúng bảng ID. Không Homing khi dây đang tuột, thả khỏi puly hoặc cơ khí còn tháo rời.
2. Để bàn tay có khoảng trống, sẵn sàng ngắt 6 V. Kiểm tra nhiệt độ trước khi chạy.
3. Giữ **position streaming OFF**, bấm **Homing một lần**.
4. Quan sát suốt quy trình. Firmware có thể bỏ qua lệnh điều khiển khác khi Homing; nếu kẹt bất thường hoặc dây tuột, ngắt 6 V thay vì chờ nút Pause có tác dụng.
5. Chờ RX Log báo ACK hoàn tất; tùy phiên bản và cơ khí có thể cần đến khoảng ba phút. Nếu timeout, không bấm lặp ngay: kiểm tra nguồn, COM và trạng thái cơ khí.
6. Đọc **GET_TEMP**, **GET_POS**, **GET_CURR**; nhìn lại từng ngón. ACK chỉ xác nhận quy trình kết thúc, không chứng minh mọi mốc đã đúng.
7. Bản GUI của dự án vẫn để streaming OFF sau Homing. Kiểm tra tư thế và các slider trước khi bấm Start.

**Set Speed/Set Torque trong GUI không bảo đảm hạn chế lực/tốc độ của Homing.** Quy trình Homing có các giá trị riêng trong firmware. Không coi việc đặt lực thấp ở GUI là một cơ chế giới hạn Homing.

### Chỉnh nhỏ bằng Trim Servo

- Dừng streaming trước khi Trim; ghi lại giá trị đã chỉnh để có thể kiểm tra lại.
- Chọn đúng ID. Bắt đầu bằng bước nhỏ, chẳng hạn **1–5°**, rồi thử chuyển động nhỏ và quan sát.
- Dấu `+`/`-` là thay đổi tọa độ servo; không có một dấu duy nhất luôn tương ứng với “mở hơn” cho mọi kênh.
- Trim thay đổi **mốc mở**. Nếu mức 1 vẫn chưa gập hết, không tiếp tục Trim đầu mở để cố chữa đầu đóng.
- Không dùng Trim để bù dây luồn sai, dây liên động chùng, nút trượt hoặc puly bị kẹt.
- Mốc Trim được firmware lưu; chạy lại Homing có thể thay các mốc thủ công bằng mốc mới.

### Calibrate Mid và khả năng tương thích

GUI/source SDK hiện có nút **Calibrate Mid**, nhưng không thể suy ra file `.bin` v0.2.0 đang chạy hỗ trợ tính năng này chỉ từ việc thấy nút. Chỉ dùng khi đã xác nhận firmware tương thích và hiểu việc thay đổi tọa độ servo. Nếu không có ACK, không gửi lặp.

Hiệu chỉnh điểm giữa, mốc mở và mốc đóng là các việc khác nhau. Sau mọi thay đổi tọa độ, cần kiểm tra lại trước khi cho lệnh hết biên.

## 6. Điều khiển vị trí bằng slider

Chỉ thực hiện khi cơ khí và mốc đã được xác nhận.

1. Khi streaming OFF, kiểm tra giá trị **cả bảy slider**, không chỉ thanh định di chuyển. Chọn tư thế khởi đầu đã kiểm chứng không ép vào chặn.
2. Đặt giới hạn tốc độ/lực thấp cho các kênh cần thử bằng **Set Speed** và **Set Torque**, chờ ACK. Các con số này là đơn vị lệnh, không phải phần trăm, độ/giây, N·m hay mA.
3. Bấm **Start Position Commands**. Toàn bộ slider được gửi ngay ở tần số đã chọn; không có bảo đảm tự tăng tốc/đi dần từ tư thế hiện tại.
4. Với kênh đã có mốc đúng, thử dịch nhỏ khoảng **0,02–0,05** mỗi lần. Quan sát rồi mới tăng tiếp.
5. Dùng **Pause Position Commands** khi cần dừng gửi mục tiêu mới. Servo vẫn có thể giữ lực ở mục tiêu cuối; muốn ngắt động lực chắc chắn thì tắt 6 V.

Theo quy ước hiệu chỉnh, **0 là mốc mở, 1 là mốc đóng**. Nếu mốc chưa đúng, 0/1 chỉ là hai đầu phần mềm, không phải hai giới hạn cơ khí đã được xác nhận.

GUI quy đổi slider 0–1 sang góc khớp trước khi gửi:

| Slider | 0 → 1 tương ứng |
|---|---|
| 0 thumb_abduction | 0° → 100° |
| 1 thumb_flex | 0° → 55° |
| 2 thumb_tendon, 3 index, 4 middle, 5 ring, 6 pinky | 0° → 90° |

Hai số `0.000` và `1.000` ở hai đầu mỗi hàng chỉ là nhãn min/max cố định. Số do **GET_POS** in ra là vị trí **cơ cấu** chuẩn hóa 0–1, không cùng thang với slider khớp. Ví dụ slider index 0,5 không cho GET_POS bằng 0,5.

Giới hạn Set Speed/Set Torque có thể trở về giá trị mặc định khi ESP32 khởi động lại; đặt lại trước một phiên thử mới. Hộp Set Torque của GUI giới hạn nhập **0–1000**; nếu thấy giá trị gợi ý 1023, sửa về một giá trị hợp lệ thay vì coi đó là mức nên dùng.

Ba chuyển động ngón cái có liên hệ cơ khí. Trong GUI hiện tại, các slider được chuyển qua mô hình khớp–cơ cấu rồi gửi một frame cho cả bảy servo; thay một thanh ngón cái có thể kéo theo thay đổi lệnh ở cơ cấu ngón cái khác. Không lấy điều đó làm bằng chứng duy nhất rằng ID bị đảo.

## 7. Theo dõi nhiệt độ, dòng và dữ liệu phản hồi

Ưu tiên đọc riêng **GET_TEMP**, **GET_CURR**, **GET_POS** khi kiểm tra.

- Thứ tự các phần tử luôn là **ID 0, 1, 2, 3, 4, 5, 6**. Ví dụ nhiệt độ ở phần tử thứ năm là ID 4.
- `GET_POS` trên GUI là vị trí chuẩn hóa 0–1, không phải số encoder 0–4095. Không so trực tiếp nó với giá trị raw của công cụ chẩn đoán.
- SDK hiện nhân giá trị dòng có dấu với **6,5** và hiển thị theo mA. Công cụ raw từng dùng trong phiên lắp không thực hiện cùng phép đổi. Không so trực tiếp hai loại số, hoặc coi lệnh lực 250 là dòng 250 mA. Cần kiểm chứng hệ số theo đúng model servo trước khi dùng ngưỡng dòng tuyệt đối.
- Dùng độ lớn dòng để quan sát tải; dấu âm/dương thể hiện chiều theo giao thức. Tải tăng mà vị trí không tiến thêm cần được kiểm tra, không tự kết luận là chặn cơ khí hợp lệ.
- Trong firmware đã kiểm tra, bộ đọc theo nhóm chỉ cập nhật đủ dữ liệu khi nhận được cả bảy ID. Thiếu servo có thể khiến log giữ giá trị cũ/toàn số 0. Có phản hồi USB không bảo đảm mọi servo đang có nguồn.
- `GET_ALL` ở source GUI hiện tại tính lại trường POS không đúng cách chuẩn hóa của `GET_POS`; dùng **GET_POS riêng** để đánh giá vị trí.

Trong giai đoạn lắp/căn của bàn tay này, nếu nhiệt độ tăng nhanh khi đứng yên hoặc lên khoảng **45–50°C**, nên dừng, cắt 6 V và kiểm tra tải/dây trước khi tiếp tục. Đây là mốc theo dõi thận trọng cho việc căn chỉnh, **không phải thông số ngắt nhiệt của hãng**. Không chờ đến lúc servo tự bảo vệ mới dừng.

## 8. Những thao tác cần tránh nhầm

- **Torque Control:** slider lực gửi lệnh tới cả bảy servo. Không dùng để thử riêng một ngón khi chưa hiểu chế độ; đưa nó về 0 cũng không bảo đảm tắt lực trên mọi phiên bản firmware.
- **Start/Pause:** không phải công tắc bật/tắt torque của servo.
- **Set to Open Position:** có chuyển động, không phải một lệnh thả trôi.
- **ZERO_ALL:** gửi mọi khớp về giới hạn dưới 0°. Ngày 03/11/2026, sau ZERO_ALL, thumb_abd (ID 0) đứng yên nhưng dòng khoảng 1900 đơn vị và nóng tới 60 °C vì bị ghì vào điểm chặn. Giữ ở khoảng 5° thì dòng còn khoảng 60. Không dùng ZERO_ALL làm tư thế nghỉ.
- **Nạp lại cùng firmware:** không tự xóa hết dữ liệu hiệu chỉnh trong NVS hoặc offset EEPROM nằm trong từng servo.
- **Đổi ID:** không hiệu chỉnh góc tay đòn hay chiều dài dây. Không chạy lại các lệnh `swap01`/`swap12` chỉ để “kiểm tra”; chúng sẽ đảo ngược ID đang đúng.
- **Các script chẩn đoán:** `servo_diag.py` và `servo_release_status.py` cần firmware riêng, không dùng trực tiếp với firmware chuẩn v0.2.0. Không nạp firmware reset/chẩn đoán cho một phiên vận hành bình thường.

## 9. Kết thúc phiên sử dụng

1. Nếu hành trình đã kiểm chứng và không có lỗi cơ khí, đưa bàn tay về tư thế nghỉ thuận tiện bằng chuyển động chậm.
2. Bấm **Pause Position Commands**.
3. **Tắt nguồn 6 V** để ngắt động lực; đỡ cơ cấu nếu nó có thể tự hồi/rơi khi mất lực.
4. Bấm **Disconnect**, đóng GUI. Sau đó mới tháo USB hoặc chỉnh dây/cơ khí.

Nếu đang kẹt, dây tuột hoặc chuyển động bất thường, **ngắt 6 V trước**, không cố ra lệnh mở toàn bộ để xử lý.

## 10. Xử lý lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Không thấy COM11 | Kiểm tra USB có truyền dữ liệu, bấm Refresh; xem Device Manager và chọn COM mới nếu đã đổi |
| `Access is denied` / port busy | Đóng Serial Monitor, script hoặc GUI khác đang giữ cổng; chỉ mở một chương trình |
| `WriteFile failed` / USB mất kết nối | Pause/đóng kết nối; nếu cơ khí đang chịu tải, cắt 6 V. Kiểm tra cáp USB và nguồn; không gửi lặp liên tục |
| Connect được nhưng servo không phản hồi | Kiểm tra nguồn 6 V, giắc và đúng firmware; USB phản hồi không đồng nghĩa servo có nguồn |
| GET_POS toàn 0 hoặc số không đổi | Kiểm tra đủ bảy ID/nguồn, không coi ngay đó là mốc home thật |
| `[err] GET_POS: object of type 'NoneType' has no len()` | SDK không nhận đủ 16 byte trong 10 ms nên trả `None`; xem dòng `Timeout...`/`Invalid response...` ở cửa sổ console của ChayGUI. Thường do robot đang Homing sau khi cấp nguồn (firmware bỏ qua mọi lệnh), chưa có 6 V, hoặc phản hồi trễ; đợi rồi bấm lại |
| Kéo slider nhưng tay không chuyển động | Streaming đang OFF; bấm **Start Position Commands**. Sau Homing/Set ID/Calibrate Mid/Torque Control/kết nối lại, streaming tự tắt |
| Nhiệt độ đọc toàn 0 °C | 6 V đã ngắt; ESP32 vẫn trả lời qua USB nhưng servo không có dữ liệu |
| Ngón giữa (ID 4) nóng nhất, dòng cao hơn hẳn ngón khác ở cùng góc | Đo ngày 03/11/2026: ở 20° dòng khoảng 470 so với 50–80 ở các ngón khác, nhiệt 57–68 °C. Tắt 6 V, kiểm tra dây gân, ma sát và kẹt của ngón giữa |
| Slider bằng 1 nhưng ngón chưa gập hết | Kiểm tra mốc, chiều quấn, chiều dài dây, dây liên động và tải; không mặc định đổi ID hoặc tăng lực tối đa |
| Ngón cái không duỗi | Xác nhận ID 1/2 đúng, dây không quá căng/kẹt và lò xo hồi làm việc; Homing lại chỉ sau khi cơ khí đã ổn |
| Servo nóng khi đứng yên | Cắt 6 V, để nguội, kiểm tra mục tiêu đang ép vào chặn hoặc dây quá căng |
| Homing có ACK nhưng tư thế sai | Dừng, kiểm tra từng cơ cấu; ACK không phải chứng nhận hiệu chỉnh thành công |
| Đổi được ID nhưng servo chưa quay | Việc đổi ID có thể tắt torque; không suy ra servo hỏng. Không dùng Homing cưỡng bức chỉ để bật lại lực |

## 11. Dùng Python SDK

Đóng GUI trước khi chạy Python để nhường cổng COM. Khởi tạo SDK mở cổng serial; việc đóng SDK chỉ đóng cổng, không phải lệnh tắt lực.

### Ví dụ chỉ đọc nhiệt độ

```python
from aero_open_sdk.aero_hand import AeroHand

hand = AeroHand(port="COM11", baudrate=921600)
try:
    print("Nhiệt độ ID 0–6:", hand.get_actuator_temperatures())
finally:
    hand.close()
```

Ví dụ không gọi Homing hoặc lệnh vị trí. Tuy nhiên việc mở cổng/nguồn có thể gây reset tùy đường điều khiển USB; vẫn chuẩn bị cơ khí cho khả năng firmware tự Homing khi ESP32 khởi động.

### Các hàm điều khiển cần biết

| Hàm | Ý nghĩa |
|---|---|
| `hand.send_homing(timeout_s=175.0)` | Có chuyển động tìm mốc; chờ ACK |
| `hand.set_speed(id, value)` | Giới hạn tốc độ kênh trong điều khiển vị trí |
| `hand.set_torque(id, value)` | Giới hạn lực kênh trong điều khiển vị trí |
| `hand.get_joint_positions_compact()` | Đọc tư thế khớp dạng bảy giá trị theo mô hình SDK |
| `hand.set_joint_positions(pose)` | Gửi một tư thế khớp bằng **độ**, nhận vector 7 hoặc 16 phần tử; không phải vector 0–1 của GUI |
| `hand.set_actuations(values)` | Điều khiển cơ cấu trực tiếp bằng độ; dễ bỏ qua liên hệ cơ khí ngón cái, chỉ dùng khi hiểu mô hình |
| `hand.close()` | Đóng serial, không tự thả trôi |

Ưu tiên API khớp `set_joint_positions` khi điều khiển bàn tay hoàn chỉnh. Mỗi lệnh tư thế vẫn gửi mục tiêu cho cả bảy servo. Chỉ chạy các ví dụ `run_sequence.py`/`power_grasp.py` sau khi đã kiểm tra toàn bộ hành trình và hiệu chỉnh.

Bảy khớp rút gọn của `set_joint_positions` (đơn vị độ): `[thumb_abd 0–100, thumb_flex 0–55, thumb_tip 0–90, index, middle, ring, pinky 0–90]`. Giá trị ngoài giới hạn bị SDK cắt về giới hạn. Chuyển động mượt dùng `hand.run_trajectory([(tư_thế, 0), (tư_thế_mới, số_giây), ...])`, gửi ở 100 Hz.

### Ví dụ có sẵn

| File | Nội dung |
|---|---|
| `examples/tim_cong.py` | Tự tìm cổng Aero Hand (USB VID `303A`, xác nhận bằng GET_POS), in góc khớp và nhiệt độ. Chỉ đọc |
| `examples/dieu_khien_co_ban.py --port COM7` | Đọc góc, nhiệt độ, dòng. Thêm `--move` để gập nhẹ 4 ngón 30° rồi mở lại; dừng nếu servo ≥ 45 °C và hỏi xác nhận trước |
| `examples/dieu_khien_camera.py` | Điều khiển bằng webcam; xem **HUONG_DAN_CAMERA.md** |

Mở cổng COM làm ESP32 khởi động lại (in `[BOOT]...`). Lần đọc đầu có thể báo `Invalid response ... got 91`; thử lại là được. Đây là reset không mất nguồn nên firmware không tự Homing.

## 12. Nạp lại firmware khi cần

1. Tắt 6 V, giữ USB, đóng các chương trình khác đang dùng COM.
2. GUI → chọn COM → **Upload Firmware**.
3. Chọn đúng file ứng dụng tay trái: `C:\AeroHand_Student\aero-hand-open\firmware\main\bin\firmware_v0.2.0_lefthand.bin`.
4. Công cụ GUI ghi ở **0x10000**. Không thay bằng file merged/bootloader/partition.
5. Chờ báo nạp thành công. Giữ 6 V tắt đến khi đã chuẩn bị cơ khí và tư thế làm việc.
6. Khi kết nối lại, kiểm tra GUI vẫn ở trạng thái streaming OFF. Không mặc định rằng nạp firmware đã hiệu chỉnh lại bàn tay.

## 13. Nguồn đối chiếu

- [Hướng dẫn phần cứng chính thức](https://docs.tetheria.ai/docs/hardware_setup/).
- [Cài đặt và vận hành SDK/GUI](https://docs.tetheria.ai/docs/software_setup/).
- [Các chức năng GUI và quy trình đặt ID](https://docs.tetheria.ai/docs/gui/).
- Source GUI tại `aero-hand-open/sdk/src/aero_open_sdk/gui.py`, SDK tại `aero_hand.py`, firmware tại `aero-hand-open/firmware/main/`.
- Bản GUI trong dự án đã có nút Start/Pause Position Commands; giao diện tải mới từ pip có thể khác. Mã source và `.bin` được phát hành không nhất thiết cùng mức tính năng.

**Trình tự nhớ nhanh:** kiểm tra cơ khí → chuẩn bị cho khả năng Homing lúc khởi động → Connect với streaming OFF → xác nhận mốc và dữ liệu → thử nhỏ → mới vận hành toàn hành trình → Pause → tắt 6 V → Disconnect.
