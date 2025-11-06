from __future__ import annotations

import json
import socket
import threading

import cv2
# from DobotEDU import *


UDP_IP = "127.0.0.1"  # Change to robot server IP if remote

UDP_PORT = 9000

UDP_ADDRESS = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

busy_flag = False


def send_message(msg):
    data = json.dumps(msg)
    sock.sendto(data.encode("utf-8"), UDP_ADDRESS)
    print(f"Sent message: {data}")


def receive_message():
    print(f"waiting for message from {UDP_ADDRESS[0]}")
    data, addr = sock.recvfrom(1024)
    msg = json.loads(data.decode("utf-8"))
    print(f"Received message from {addr}: {msg}")


def do_camera():
    global busy_flag
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
        # Show the frame
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if busy_flag:
            cv2.putText(
                frame,
                "Busy",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )
        else:
            cv2.putText(
                frame,
                "Ready",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
        cv2.imshow("Camera Preview", frame)

    cap.release()
    cv2.destroyAllWindows()


def send_and_wait(msg):
    send_message(msg)
    receive_message()


def do_work():
    global busy_flag
    busy_flag = True
    send_and_wait({"action": "do_work"})
    busy_flag = False


def send_key_press(key):
    send_message({"action": "key_press", "key": key})


def main():
    key = ""
    menu = """
    Choose:
        w - do_work
        q - quit
    """
    actions = {
        "w": do_work,
        "?": lambda: print(menu),
    }
    # thread = threading.Thread(target=do_camera, daemon=True)
    # thread.start()
    while True:
        key = input(menu).strip()

        if key == "q":
            break

        action = actions.get(key)

        if callable(action):
            action()
        else:
            send_key_press(key)

    print("Bye bye")


if __name__ == "__main__":
    main()
