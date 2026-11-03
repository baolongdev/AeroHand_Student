"""Tu tim cong COM cua Aero Hand (chi doc, khong gui lenh chuyen dong).

Chay rieng de xem ket qua:
    .venv\\Scripts\\python.exe examples\\tim_cong.py
"""
import time

from serial.tools import list_ports

ESPRESSIF_VID = 0x303A   # ESP32-S3 tren ban tay Aero Hand


def cong_ung_vien() -> list[str]:
    """Cac cong co chip Espressif truoc, sau do cac cong USB khac (bo qua Bluetooth)."""
    ports = list_ports.comports()
    esp = [p.device for p in ports if p.vid == ESPRESSIF_VID]
    other = [p.device for p in ports if p.vid is not None and p.vid != ESPRESSIF_VID]
    return esp + other


def mo_ban_tay(port: str | None = None, verbose: bool = True):
    """Mo AeroHand. port=None/'auto' -> tu tim. Tra ve (hand, port) hoac (None, None)."""
    from aero_open_sdk.aero_hand import AeroHand

    candidates = cong_ung_vien() if port in (None, "", "auto") else [port]
    if verbose:
        print("Cong can thu:", candidates or "khong co")
    for dev in candidates:
        try:
            hand = AeroHand(port=dev)
        except Exception as e:
            if verbose:
                print(f"  {dev}: khong mo duoc ({e})")
            continue
        time.sleep(0.2)
        for _ in range(5):                  # thu doc vi tri vai lan (lenh chi doc)
            if hand.get_actuations() is not None:
                if verbose:
                    print(f"  {dev}: Aero Hand tra loi -> dung cong nay")
                return hand, dev
            time.sleep(0.1)
        if verbose:
            print(f"  {dev}: khong tra loi GET_POS (dang homing? chua cap 6 V? GUI dang giu cong?)")
        hand.close()
    return None, None


if __name__ == "__main__":
    hand, dev = mo_ban_tay()
    if hand is None:
        raise SystemExit("Khong tim thay Aero Hand. Dong GUI, kiem tra cap USB va nguon 6 V.")
    try:
        names = ["thumb_abd", "thumb_flex", "thumb_tip", "index", "middle", "ring", "pinky"]
        pos = hand.get_joint_positions_compact()
        temp = hand.get_actuator_temperatures()
        print(f"\nAero Hand o {dev}")
        for i, n in enumerate(names):
            p = f"{pos[i]:7.1f}" if pos else "      -"
            t = f"{temp[i]:5.0f}" if temp else "    -"
            print(f"  {n:<11} goc {p} do   nhiet {t} C")
    finally:
        hand.close()
