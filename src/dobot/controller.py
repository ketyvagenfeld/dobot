# from DobotEDU import *
import socket
import json
import time

import cv2
import numpy as np
import threading


UDP_IP = "127.0.0.1"
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
    return msg


def send_and_wait(msg):
    send_message(msg)
    return receive_message()


threshold_value = 127


def do_camera():
    global busy_flag, threshold_value
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    print(f"Starting threshold = {threshold_value}")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            continue

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bw_image = cv2.threshold(
            gray_image, threshold_value, 255, cv2.THRESH_BINARY
        )
        median_blurred_img = cv2.medianBlur(bw_image, 5)
        contours, _ = cv2.findContours(
            median_blurred_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        color_image = cv2.cvtColor(median_blurred_img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(color_image, contours, -1, (0, 255, 0), 2)
        colorframe = frame.copy()

        for cnt in contours:
            contour_area = cv2.contourArea(cnt)
            rect = cv2.minAreaRect(cnt)  # rect = ((cx, cy), (w, h), angle)
            width = rect[1][0]
            height = rect[1][1]

            if width == 0 or height == 0:
                continue

            ratio = contour_area / (width * height)
            perimeter = cv2.arcLength(cnt, True)

            if perimeter == 0:
                continue

            circularity = 4 * np.pi * (contour_area / (perimeter * perimeter))
            cx, cy = int(rect[0][0]), int(rect[0][1])

            if frame is not None:
                cv2.putText(
                    colorframe,
                    f"C:{circularity:.2f}",
                    (cx - 30, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 255),
                    1,
                )
                cv2.putText(
                    colorframe,
                    f"R:{ratio:.2f}",
                    (cx - 30, cy + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                )

        cv2.drawContours(colorframe, contours, -1, (0, 255, 0), 2)

        cv2.putText(
            colorframe,
            f"t: {threshold_value}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 0),
            3,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            "Busy" if busy_flag else "Ready",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255) if busy_flag else (0, 255, 0),
            2,
        )
        cv2.imshow("Camera Preview", colorframe)
    cap.release()
    cv2.destroyAllWindows()


def do_some_work():
    print("starting job...")
    time.sleep(5)
    print("job finished")


thread = threading.Thread(target=do_some_work(), daemon=True)
thread.start()


def inc_threshold():
    global threshold_value
    threshold_value = min(threshold_value + 5, 255)
    print(f"Threshold increased to {threshold_value}")


def dec_threshold():
    global threshold_value
    threshold_value = max(threshold_value - 5, 0)
    print(f"Threshold decreased to {threshold_value}")


def do_work():
    global busy_flag
    busy_flag = True
    send_and_wait({"action": "do_work"})
    busy_flag = False


# --- NEW: user actions for the assignment ---
def pick_place_rect():
    global busy_flag
    busy_flag = True
    send_and_wait({"action": "pick_place_rect"})
    busy_flag = False


def pick_place_round():
    global busy_flag
    busy_flag = True
    send_and_wait({"action": "pick_place_round"})
    busy_flag = False


def go_wait():
    global busy_flag
    busy_flag = True
    send_and_wait({"action": "go_wait"})
    busy_flag = False


def main():
    import threading

    menu = """
    Choose:
        w - do_work
        r - pick & place RECT
        o - pick & place ROUND
        h - go to WAIT point
        q - quit
        + - increase
        - - decrease
    """
    actions = {
        "w": do_work,
        "r": pick_place_rect,
        "o": pick_place_round,
        "h": go_wait,
        "+": inc_threshold,
        "-": dec_threshold,
    }

    thread = threading.Thread(target=do_camera, daemon=True)
    thread.start()

    while True:
        key = input(menu).strip().lower()
        action = actions.get(key)

        if key == "q":
            break

        if callable(action):
            action()
            continue

        send_message({"action": "key_press", "key": key})

    print("Bye bye")


if __name__ == "__main__":
    main()
