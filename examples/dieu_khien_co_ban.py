"""Vi du dung Aero Hand SDK: doc trang thai, va (tuy chon) cu dong ngon cham, nhe.

Cach chay (dong GUI truoc de nhuong cong COM):
    .venv\\Scripts\\python.exe examples\\dieu_khien_co_ban.py --port COM7          # chi doc
    .venv\\Scripts\\python.exe examples\\dieu_khien_co_ban.py --port COM7 --move   # co chuyen dong
"""
import argparse
import time

from aero_open_sdk.aero_hand import AeroHand

# Thu tu 7 khop rut gon (don vi: DO), dung cho set_joint_positions / run_trajectory:
#   0 thumb_cmc_abd  (0..100)   - dang ngon cai
#   1 thumb_cmc_flex (0..55)    - gap goc ngon cai
#   2 thumb_tendon   (0..90)    - cong dau ngon cai
#   3 index  4 middle  5 ring  6 pinky  (0..90) - gap ngon
NAMES = ["thumb_abd", "thumb_flex", "thumb_tip", "index", "middle", "ring", "pinky"]

MO_TAY = [0, 0, 0, 0, 0, 0, 0]            # tay mo (gioi han duoi)
GAP_NHE = [0, 0, 0, 30, 30, 30, 30]       # 4 ngon gap 30 do, ngon cai dung yen

NHIET_DO_MAX = 45.0  # C - moc dung than trong theo huong dan cua lop


def in_trang_thai(hand: AeroHand) -> list[float] | None:
    pos = hand.get_joint_positions_compact()   # do (7 khop)
    temp = hand.get_actuator_temperatures()    # do C, ID 0..6
    curr = hand.get_actuator_currents()        # luu y: he so mA chua chac dung, xem nhu tuong doi
    if pos is None or temp is None:
        print("Khong doc duoc du lieu - kiem tra cong COM, nguon 6 V, homing da xong chua.")
        return None
    print(f"{'khop':<11}{'goc(do)':>9}{'temp(C)':>9}{'dong':>9}")
    for i, name in enumerate(NAMES):
        c = f"{curr[i]:.0f}" if curr else "-"
        print(f"{name:<11}{pos[i]:>9.1f}{temp[i]:>9.0f}{c:>9}")
    return temp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM7")
    ap.add_argument("--move", action="store_true", help="cho phep chuyen dong (mo -> gap nhe -> mo)")
    args = ap.parse_args()

    hand = AeroHand(port=args.port)
    try:
        time.sleep(0.2)
        temp = in_trang_thai(hand)
        if not args.move or temp is None:
            return

        if max(temp) >= NHIET_DO_MAX:
            print(f"Servo nong ({max(temp):.0f} C) - khong chay. Ngat 6 V va kiem tra.")
            return
        if input("Ban tay se cu dong. San sang ngat 6 V? Go 'y' de tiep tuc: ").strip().lower() != "y":
            return

        # Moi phan tu: (tu the 7 khop, thoi gian di toi tu the do - giay). Diem dau chi la diem xuat phat.
        quy_dao = [
            (MO_TAY, 0.0),
            (GAP_NHE, 2.0),   # gap cham trong 2 s
            (MO_TAY, 2.0),    # mo lai trong 2 s
        ]
        hand.run_trajectory(quy_dao)   # gui lenh 100 Hz, noi suy tuyen tinh
        time.sleep(0.5)
        print("\nSau khi chay:")
        in_trang_thai(hand)
    finally:
        hand.close()   # chi dong cong COM, KHONG tat luc giu servo


if __name__ == "__main__":
    main()
