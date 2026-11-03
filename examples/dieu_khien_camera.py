"""Doc goc khop ngon tay nguoi bang camera (OpenCV + MediaPipe) va dieu khien Aero Hand theo.

Chay (dong GUI truoc de nhuong cong COM):
    .venv\\Scripts\\python.exe examples\\dieu_khien_camera.py               # TU TIM cong Aero Hand (CHUA gui lenh)
    .venv\\Scripts\\python.exe examples\\dieu_khien_camera.py --port COM7   # chi dinh cong
    .venv\\Scripts\\python.exe examples\\dieu_khien_camera.py --port none   # chi xem camera, KHONG noi ban tay

Chi nhan TAY TRAI (cung ben voi ban tay robot). Doi bang --hand right.
Mac dinh KHOA ngon cai, chi dieu khien 4 ngon. Them --thumb de dieu khien ca ngon cai.

Phim (bam khi cua so camera dang duoc chon):
    O      : hieu chinh "tay MO"   (xoe thang cac ngon)
    F      : hieu chinh "tay NAM"  (nam chat)
    SPACE  : bat dau dong bo -> dat tay KHOP vach trang (vi tri robot) -> tu dong dieu khien.
             Bam lai de dung.
    R      : xoa hieu chinh, ve mac dinh
    Q, ESC : thoat -> robot tu tu ve HOME (tat ca khop 0 do = tay mo)
"""
import argparse
import json
import math
import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

# Thu tu 7 khop rut gon cua Aero Hand (don vi DO) - giong set_joint_positions()
NAMES = ["thumb_abd", "thumb_flex", "thumb_tip", "index", "middle", "ring", "pinky"]
LIMITS = [100.0, 55.0, 90.0, 90.0, 90.0, 90.0, 90.0]   # 0 = tay mo, LIMIT = gap het
# Goc nho nhat gui toi robot. thumb_abd o 0 do bi ep vao diem chan co khi (dong rat cao, servo nong)
# -> gioi han 5 do. Chinh neu ban tay cua ban khac.
ROBOT_MIN = [5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
HOME = list(ROBOT_MIN)                                 # tu the home khi thoat

# Gia tri "tho" (do) do tu camera o tu the mo / nam. Bam O / F de do lai cho tay cua ban.
DEFAULT_OPEN = [45.0, 150.0, 20.0, 15.0, 15.0, 15.0, 15.0]
DEFAULT_CLOSE = [15.0, 60.0, 110.0, 230.0, 230.0, 230.0, 230.0]
CALIB_VERSION = 2   # doi cach do thumb_flex -> file hieu chinh cu khong dung duoc nua
CALIB_FILE = Path(__file__).with_name("hieu_chinh_camera.json")

TEMP_MAX_C = 45.0       # dung gui lenh khi servo nong hon muc nay (moc than trong cua lop)
TEMP_PERIOD_S = 2.0     # chu ky doc nhiet do
LOST_HAND_S = 0.5       # mat tay qua thoi gian nay -> giu nguyen tu the
SYNC_TOL_DEG = 10.0     # sai lech cho phep giua tay ban va robot de "bat tay"
SYNC_HOLD_S = 0.5       # phai giu khop trong thoi gian nay moi bat dau dieu khien
HOME_SPEED = 60.0       # toc do ve home khi thoat (do/giay)
POS_PERIOD_S = 0.1      # chu ky doc vi tri THAT cua robot (10 Hz)
ERR_OK_DEG = 10.0       # sai lech <= muc nay: XANH
ERR_BAD_DEG = 40.0      # sai lech >= muc nay: DO (o giua: chuyen dan qua VANG)

FINGERS = {3: (5, 6, 7, 8), 4: (9, 10, 11, 12), 5: (13, 14, 15, 16), 6: (17, 18, 19, 20)}
WIN = "Aero Hand - camera"

IDLE, SYNC, ARMED = "IDLE", "SYNC", "ARMED"


# ---------------------------------------------------------------- hinh hoc
def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _angle(u, v) -> float:
    """Goc giua hai vector (do)."""
    c = float(np.dot(_unit(u), _unit(v)))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def _bend(p, a, b, c) -> float:
    """Do gap tai diem b: 0 = thang hang a-b-c."""
    return _angle(p[b] - p[a], p[c] - p[b])


def raw_features(p: np.ndarray) -> list[float]:
    """p: 21x3 toa do the gioi (m) cua MediaPipe. Tra ve 7 gia tri tho (do)."""
    out = [0.0] * 7
    thumb_meta = p[2] - p[1]
    out[0] = _angle(thumb_meta, p[5] - p[0])                                   # dang ngon cai
    # gap goc ngon cai qua long ban tay: khoang cach dau ngon cai -> goc ngon ut, chia kich thuoc ban tay
    palm = float(np.linalg.norm(p[9] - p[0])) or 1e-6
    out[1] = 100.0 * float(np.linalg.norm(p[4] - p[17])) / palm
    out[2] = _bend(p, 1, 2, 3) + _bend(p, 2, 3, 4)                            # cong ngon cai
    for j, (mcp, pip, dip, tip) in FINGERS.items():                             # 4 ngon: tong 3 khop
        out[j] = _bend(p, 0, mcp, pip) + _bend(p, mcp, pip, dip) + _bend(p, pip, dip, tip)
    return out


# ---------------------------------------------------------------- hieu chinh
def load_calib():
    try:
        d = json.loads(CALIB_FILE.read_text(encoding="utf-8"))
        if d.get("version") == CALIB_VERSION and len(d["open"]) == 7 and len(d["close"]) == 7:
            return d["open"], d["close"]
    except Exception:
        pass
    return list(DEFAULT_OPEN), list(DEFAULT_CLOSE)


def save_calib(open_raw, close_raw):
    CALIB_FILE.write_text(json.dumps({"version": CALIB_VERSION, "open": open_raw, "close": close_raw},
                                     indent=2), encoding="utf-8")


def to_robot(raw, open_raw, close_raw) -> list[float]:
    """Quy doi gia tri tho -> goc khop robot (do), 0 = mo, LIMIT = gap."""
    out = []
    for i in range(7):
        span = close_raw[i] - open_raw[i]
        if abs(span) < 5.0:                       # hieu chinh hong -> dung mac dinh
            span = DEFAULT_CLOSE[i] - DEFAULT_OPEN[i]
            t = (raw[i] - DEFAULT_OPEN[i]) / span
        else:
            t = (raw[i] - open_raw[i]) / span
        out.append(max(ROBOT_MIN[i], max(0.0, min(1.0, t)) * LIMITS[i]))
    return out


# ---------------------------------------------------------------- robot
def read_robot_pose(hand) -> list[float] | None:
    cur = hand.get_joint_positions_compact()
    if cur is None:
        return None
    return [max(0.0, min(L, c)) for c, L in zip(cur, LIMITS)]


def go_home(hand, last_sent, controlled):
    """Dua cac khop dang dieu khien tu tu ve HOME (0 do). Khop bi khoa (ngon cai) giu nguyen
    de khong ep servo vao diem chan co khi o 0 do."""
    start = read_robot_pose(hand) or last_sent
    if start is None:
        print("Khong doc duoc vi tri robot -> khong ve HOME.")
        return
    home = [HOME[i] if i in controlled else start[i] for i in range(7)]
    dist = max(abs(s - h) for s, h in zip(start, home))
    duration = max(0.5, dist / HOME_SPEED)
    print(f"Dang ve HOME trong {duration:.1f} s ...")
    hand.run_trajectory([(start, 0.0), (home, duration)])
    time.sleep(0.3)
    print("Da ve HOME (tay mo).")


# ---------------------------------------------------------------- ve
def err_color(e: float):
    """Mau BGR theo sai so: xanh -> vang -> do."""
    t = max(0.0, min(1.0, (e - ERR_OK_DEG) / (ERR_BAD_DEG - ERR_OK_DEG)))
    green, yellow, red = (0, 200, 0), (0, 220, 220), (0, 0, 230)
    a, b, k = (green, yellow, t * 2) if t < 0.5 else (yellow, red, (t - 0.5) * 2)
    return tuple(int(a[c] + (b[c] - a[c]) * k) for c in range(3))


def draw_panel(img, target, robot, state, msg, temp_max, controlled, which_hand):
    """robot: vi tri THAT cua robot (do) hoac None. Thanh ngon duoc to mau theo sai so camera-robot."""
    h, w = img.shape[:2]
    x0, y0 = 10, 10
    cv2.rectangle(img, (0, 0), (340, 40 + 22 * 7 + 50), (0, 0, 0), -1)
    title, color = {
        IDLE: ("CHUA GUI (SPACE)", (0, 200, 255)),
        SYNC: ("DAT TAY KHOP VACH TRANG", (0, 255, 255)),
        ARMED: ("DANG DIEU KHIEN", (0, 0, 255)),
    }[state]
    cv2.putText(img, title, (x0, y0 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    for i, name in enumerate(NAMES):
        y = y0 + 40 + 22 * i
        frac = target[i] / LIMITS[i]
        locked = i not in controlled
        if locked:
            label, txt_col, bar_col = f"{name:<10} KHOA", (130, 130, 130), (90, 90, 90)
        else:
            label, txt_col, bar_col = f"{name:<10}{target[i]:5.0f}", (255, 255, 255), (0, 200, 0)
            if robot is not None:   # mau theo sai so giua tay camera va robot that
                err = abs(target[i] - robot[i])
                bar_col = err_color(err)
                cv2.putText(img, f"e{err:3.0f}", (x0 + 286, y + 12), cv2.FONT_HERSHEY_PLAIN, 1.0, bar_col, 1)
        cv2.putText(img, label, (x0, y + 12), cv2.FONT_HERSHEY_PLAIN, 1.0, txt_col, 1)
        cv2.rectangle(img, (x0 + 140, y), (x0 + 280, y + 14), (80, 80, 80), 1)
        cv2.rectangle(img, (x0 + 140, y), (x0 + 140 + int(140 * frac), y + 14), bar_col, -1)
        if robot is not None:   # vach trang = vi tri THAT cua robot
            xs = x0 + 140 + int(140 * robot[i] / LIMITS[i])
            cv2.line(img, (xs, y - 2), (xs, y + 16), (255, 255, 255), 2)
    yb = y0 + 40 + 22 * 7 + 10
    if temp_max is not None:
        cv2.putText(img, f"Temp max: {temp_max:.0f} C", (x0, yb), cv2.FONT_HERSHEY_PLAIN, 1.0,
                    (0, 0, 255) if temp_max >= TEMP_MAX_C else (255, 255, 255), 1)
    if msg:
        cv2.putText(img, msg, (x0, yb + 22), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 255), 1)
    cv2.putText(img, f"Chi nhan tay {which_hand.upper()} | O:mo F:nam SPACE:dk R:reset Q:thoat",
                (10, h - 10), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)


def pick_hand(res, want_label):
    """Chon ban tay co nhan dung (Left/Right). Tra ve (world_landmarks, image_landmarks) hoac None."""
    if not res.multi_hand_world_landmarks or not res.multi_handedness:
        return None
    best, best_score = None, 0.0
    for world, img_lm, hd in zip(res.multi_hand_world_landmarks, res.multi_hand_landmarks, res.multi_handedness):
        c = hd.classification[0]
        if c.label == want_label and c.score > best_score:
            best, best_score = (world, img_lm), c.score
    return best


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="auto",
                    help="auto (mac dinh) = tu tim Aero Hand; vi du COM7; none = chi xem camera")
    ap.add_argument("--camera", type=int, default=0, help="so thu tu webcam")
    ap.add_argument("--smooth", type=float, default=0.35, help="loc 0..1 (nho = muot hon, cham hon)")
    ap.add_argument("--max-speed", type=float, default=150.0, help="toc do toi da gui toi robot (do/giay)")
    ap.add_argument("--thumb", action="store_true",
                    help="dieu khien ca ngon cai (mac dinh: KHOA ngon cai, chi dieu khien 4 ngon)")
    ap.add_argument("--hand", choices=["left", "right"], default="left", help="tay nguoi dung de dieu khien")
    ap.add_argument("--ignore-temp", action="store_true",
                    help="KHONG chan khi servo nong (van hien nhiet do). Tu chiu rui ro.")
    args = ap.parse_args()
    want_label = "Left" if args.hand == "left" else "Right"
    controlled = list(range(7)) if args.thumb else [3, 4, 5, 6]

    hand = None
    if args.port.lower() != "none":
        from tim_cong import mo_ban_tay
        hand, dev = mo_ban_tay(args.port)
        if hand is None:
            print("Khong tim thay Aero Hand -> chi xem camera (khong dieu khien).")
        else:
            print(f"Da noi {dev}. Chua gui lenh - bam SPACE trong cua so camera de bat.")
    ever_armed = False   # chi ve HOME khi thoat neu da tung dieu khien robot

    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit(f"Khong mo duoc camera {args.camera}. Thu --camera 1")

    # max_num_hands=2 de van tim duoc tay trai khi ca hai tay cung trong khung hinh
    detector = mp.solutions.hands.Hands(max_num_hands=2, model_complexity=1,
                                        min_detection_confidence=0.6, min_tracking_confidence=0.5)
    drawer = mp.solutions.drawing_utils

    open_raw, close_raw = load_calib()
    raw = None                     # gia tri tho da loc
    target = [0.0] * 7             # goc muc tieu tu camera
    sent = None                    # vi tri robot / goc dang gui (da gioi han toc do)
    state = IDLE
    matched = [False] * 7
    sync_since = None
    last_seen = 0.0
    last_t = time.perf_counter()
    last_temp_t, temp_max = 0.0, None
    last_pos_t, robot_meas = 0.0, None   # vi tri THAT cua robot, doc 10 Hz
    calib_ok = (open_raw, close_raw) != (DEFAULT_OPEN, DEFAULT_CLOSE)
    msg = "" if calib_ok else "Chua hieu chinh: bam O roi F"
    cv2.namedWindow(WIN)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Mat tin hieu camera.")
                break
            now = time.perf_counter()
            dt, last_t = now - last_t, now

            # Lat guong TRUOC khi nhan dien: MediaPipe gan nhan Left/Right theo anh da lat,
            # nen nhu vay nhan "Left" = dung tay trai that cua ban.
            frame = cv2.flip(frame, 1)
            res = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            picked = pick_hand(res, want_label)
            if picked is not None:
                world, img_lm = picked
                p = np.array([[q.x, q.y, q.z] for q in world.landmark])
                r = raw_features(p)
                raw = r if raw is None else [a + args.smooth * (b - a) for a, b in zip(raw, r)]
                target = to_robot(raw, open_raw, close_raw)
                last_seen = now
                drawer.draw_landmarks(frame, img_lm, mp.solutions.hands.HAND_CONNECTIONS)

            hand_ok = (now - last_seen) < LOST_HAND_S

            # ---- robot
            if hand is not None:
                if now - last_pos_t > POS_PERIOD_S:
                    last_pos_t = now
                    robot_meas = read_robot_pose(hand) or robot_meas

                if now - last_temp_t > TEMP_PERIOD_S:
                    last_temp_t = now
                    temps = hand.get_actuator_temperatures()
                    if temps:
                        temp_max = max(temps)
                        if temp_max >= TEMP_MAX_C and state != IDLE and not args.ignore_temp:
                            state = IDLE
                            msg = f"SERVO NONG {temp_max:.0f}C - da dung. Ngat 6V!"
                            print(msg)

                if state == SYNC:
                    # cho den khi tay ban khop vi tri robot (sent) thi moi dieu khien
                    matched = [abs(target[i] - sent[i]) <= SYNC_TOL_DEG for i in range(7)]
                    if hand_ok and all(matched[i] for i in controlled):
                        sync_since = sync_since or now
                        if now - sync_since >= SYNC_HOLD_S:
                            state, ever_armed = ARMED, True
                            msg = "Da khop - dang dieu khien. SPACE de dung"
                    else:
                        sync_since = None

                elif state == ARMED and hand_ok:
                    step = args.max_speed * dt
                    goal = list(sent)
                    for i in controlled:      # ngon bi khoa giu nguyen vi tri
                        goal[i] = target[i]
                    sent = [s + max(-step, min(step, g - s)) for s, g in zip(sent, goal)]
                    hand.set_joint_positions(sent)

            if picked is None:
                cv2.putText(frame, f"KHONG THAY TAY {args.hand.upper()}", (320, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            draw_panel(frame, target, robot_meas, state, msg, temp_max, controlled, args.hand)
            cv2.imshow(WIN, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27) or cv2.getWindowProperty(WIN, cv2.WND_PROP_VISIBLE) < 1:
                break
            elif key == ord("o") and raw is not None:
                open_raw = list(raw); save_calib(open_raw, close_raw); msg = "Da luu tu the MO"
            elif key == ord("f") and raw is not None:
                close_raw = list(raw); save_calib(open_raw, close_raw); msg = "Da luu tu the NAM"
            elif key == ord("r"):
                open_raw, close_raw = list(DEFAULT_OPEN), list(DEFAULT_CLOSE)
                CALIB_FILE.unlink(missing_ok=True); msg = "Da ve hieu chinh mac dinh"
            elif key == ord(" ") and hand is not None:
                if state != IDLE:
                    state = IDLE
                    msg = "Da dung dieu khien (servo van giu luc)"
                elif temp_max is not None and temp_max >= TEMP_MAX_C and not args.ignore_temp:
                    msg = "Servo con nong - khong bat"
                else:
                    cur = read_robot_pose(hand)
                    if cur is None:
                        msg = "Khong doc duoc vi tri robot - thu lai"
                    else:
                        sent = cur
                        state, sync_since = SYNC, None
                        msg = "Dat tay khop vach trang de bat dau"
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        if hand is not None:
            if ever_armed:
                try:
                    go_home(hand, sent, controlled)
                except Exception as e:
                    print(f"Loi khi ve HOME: {e}")
            else:
                print("Chua dieu khien robot lan nao -> khong di chuyen khi thoat.")
            hand.close()   # chi dong cong COM, KHONG tat luc servo
            print("Da dong COM. Servo van giu luc - ngat 6 V neu can tha long.")


if __name__ == "__main__":
    main()
