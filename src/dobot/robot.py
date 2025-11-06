from __future__ import annotations

import time
import json
import socket

# from DobotEDU import *


UDP_IP = "0.0.0.0"

UDP_PORT = 9000

UDP_ADDRESS = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def connect_socket():
    # Listen to external commands
    sock.bind(UDP_ADDRESS)
    print(f"Listening for UDP messages on address {UDP_IP} port {UDP_PORT}...")


def receieve_message():
    print("waiting for message...")
    data, addr = sock.recvfrom(1024)  # 1KB (2^10 Bytes)
    msg = json.loads(data.decode("utf-8"))
    print(f"Received message from {addr}.")
    print(f"message length: {len(data)}")
    print(f"message: {data}")
    return msg, addr


def send_message(msg, addr):
    data = json.dumps(msg)
    sock.sendto(data.encode("utf-8"), addr)
    print(f"Sent message to {addr}: {data}")


def do_some_work():
    print("Starting job...")
    time.sleep(5)
    print("Job finished.")


def main():
    connect_socket()
    while True:
        msg, addr = receieve_message()

        match msg["action"]:  # action == what we got from the user
            case "do_work":  # if action == 'do_work'
                do_some_work()
                send_message({"action": "work_done"}, addr)
            case "key_press":
                match msg["key"]:
                    case "h":
                        print("Hello Kety!")
                    case _:
                        print(f"Key pressed: {msg['key']}")
            case _:  # else ...
                send_message({"action": "command_unknown"}, addr)


if __name__ == "__main__":
    main()
