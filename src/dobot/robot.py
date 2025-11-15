# from DobotEDU import *
import socket, json, time

UDP_IP = "0.0.0.0"
UDP_PORT = 9000
UDP_ADDRESS = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# -------- Parameters (תעדכנו לפי הסצנה שלכם) --------
HOVER_Z = -10  # גובה בטוח מעל משטחים
PICK_Z = -65  # גובה הרמה
PLACE_Z = -55  # גובה הנחה

# מלבני
RECT_PICK_XY = (212.44, -18.3)  # נקודת איסוף מלבני
RECT_PLACE_XY = (189.04, -161.7)  # נקודת הנחת מלבני / מגדל

# עגול (הנחתי ערכים נפרדים; עדכנו אם צריך)
ROUND_PICK_XY = (212.44, -18.3)  # נקודת איסוף עגול
ROUND_PLACE_XY = (189.04, -161.7)  # נקודת הנחת עגול / המגדל

# נקודת המתנה: לא מעל המגדל/איסוף
WAIT_POSE = (160.0, -120.0, HOVER_Z, 0)  # x,y,z,r

# ----------------------------------------------------


def connect_socket():
    sock.bind(UDP_ADDRESS)
    print(f"Listening for UDP messages on address {UDP_IP} port {UDP_PORT}...")


def receieve_message():
    print("waiting for message...")
    data, addr = sock.recvfrom(1024)
    msg = json.loads(data.decode("utf-8"))
    print(f"Received message from {addr}: {msg}")
    return msg, addr


def send_message(msg, addr):
    data = json.dumps(msg)
    sock.sendto(data.encode("utf-8"), addr)
    print(f"Sent message: {data}")


# -------- Robot motion helpers --------
def goto_xy_z_r(x, y, z, r=0):
    magician.ptp(mode=0, x=x, y=y, z=z, r=r)


def hover_over(x, y):
    goto_xy_z_r(x, y, HOVER_Z, 0)


def pick_at(x, y):
    hover_over(x, y)
    goto_xy_z_r(x, y, PICK_Z, 0)
    magician.set_endeffector_suctioncup(enable=True, on=True)
    time.sleep(0.2)
    hover_over(x, y)


def place_at(x, y):
    hover_over(x, y)
    goto_xy_z_r(x, y, PLACE_Z, 0)
    magician.set_endeffector_suctioncup(enable=True, on=False)
    time.sleep(0.2)
    hover_over(x, y)


def go_wait():
    x, y, z, r = WAIT_POSE
    goto_xy_z_r(x, y, z, r)


# -------- Task primitives for the assignment --------
def pick_place_rect():
    pick_at(*RECT_PICK_XY)
    place_at(*RECT_PLACE_XY)


def pick_place_round():
    pick_at(*ROUND_PICK_XY)
    place_at(*ROUND_PLACE_XY)


def do_some_work():
    print("Starting job...")
    time.sleep(2)
    print("Job finished.")


def main():
    connect_socket()
    while True:
        msg, addr = receieve_message()
        action = msg.get("action")

        if action == "do_work":
            do_some_work()
            send_message({"ok": True, "action": "work_done"}, addr)

        # --- NEW: assignment actions ---
        elif action == "pick_place_rect":
            try:
                pick_place_rect()
                send_message({"ok": True, "action": "pick_place_rect_done"}, addr)
            except Exception as e:
                send_message({"ok": False, "error": str(e)}, addr)

        elif action == "pick_place_round":
            try:
                pick_place_round()
                send_message({"ok": True, "action": "pick_place_round_done"}, addr)
            except Exception as e:
                send_message({"ok": False, "error": str(e)}, addr)

        elif action == "go_wait":
            try:
                go_wait()
                send_message({"ok": True, "action": "at_wait_point"}, addr)
            except Exception as e:
                send_message({"ok": False, "error": str(e)}, addr)

        elif action == "key_press":
            key = msg.get("key")
            print(f"Key pressed: {key}")

        else:
            send_message({"ok": False, "action": "command_unknown"}, addr)


if __name__ == "__main__":
    main()
