#  ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import time
import random
import socket
import threading
import pickle
import colorama
from zlib import compress, decompress
from hashlib import sha256
from colorama import Fore
from _constants import *
colorama.init()


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.clients = []

    def start(self, manager):
        self.server.listen()
        print(Fore.GREEN + f"[SERVER] Started, ip: {self.ip}, port: {self.port}" + Fore.WHITE)

        while True:
            conn, addr = self.server.accept()
            client = Client(conn, addr, manager)
            self.clients.append(client)


class Client:
    header = 64
    padding = " " * header
    packet_size = 1024
    raise_recv_error = True

    def __init__(self, conn, addr, manager):
        self.conn = conn
        self.addr = addr
        self.manager = manager
        self.active = True
        self.alert("INFO", "Connected")
        threading.Thread(target=self.start).start()

    def start(self):
        self.auth()
        self.status = "IDLE"

        while self.active:
            msg = self.recv()

            try:
                if msg["type"] == "quit":
                    self.conn.close()
                    self.manager.remove(self.addr)
                    self.active = False
                    self.alert("INFO", "Disconnected")
                    return

                elif msg["type"] == "new_meeting":
                    result = self.manager.new_meeting(self, msg)
                    if result["status"]:
                        self.meeting = self.manager.meetings[result["key"]]
                        self.send({"type": "new_meeting", "status": True})
                        self.alert("INFO", "Created meeting")
                    else:
                        self.send({"type": "new_meeting", "status": False, "error": result["error"]})
                        self.alert("WARNING", "Failed to create meeting with error: " + result["error"])

                elif msg["type"] == "start_meeting":
                    if self.meeting.is_host(self):
                        self.meeting.started = True
                        self.alert("INFO", "Started meeting")

                elif msg["type"] == "chat_send":
                    self.meeting.new_chat_msg(self, msg["msg"])

                elif msg["type"] == "join_meeting":
                    result = self.manager.join_meeting(self, msg)
                    if result["status"]:
                        self.meeting = self.manager.meetings[result["key"]]
                        self.send({"type": "join_meeting", "status": True})
                        self.alert("INFO", "Joined meeting")
                    else:
                        self.send({"type": "join_meeting", "status": False, "error": result["error"]})
                        self.alert("WARNING", "Failed to join meeting with error: " + result["error"])

                elif msg["type"] == "get":
                    if msg["data"] == "attendees":
                        self.send({"type": "get", "data": self.meeting.get_names()})
                    elif msg["data"] == "info":
                        self.send({"type": "get", "data": self.meeting.get_info()})
                    elif msg["data"] == "chat":
                        self.send({"type": "get", "data": self.meeting.chat})
                    elif msg["data"] == "is_host":
                        self.send({"type": "get", "data": self.meeting.is_host(self)})
                    elif msg["data"] == "meeting_started":
                        self.send({"type": "get", "data": self.meeting.started})

                elif msg["type"] == "meeting_get":
                    self.send({"type": "meeting_get", "data": self.meeting.get_names()})
                    self.send({"type": "meeting_get", "data": self.meeting.get_videos()})

                    data = self.recv()
                    while "video_on" not in data:
                        data = self.recv()

                    if data["video_on"]:
                        self.meeting.set_video(self, data["video"])

            except Exception as e:
                e = str(e)
                error_msg = e if len(e) < 50 else e[:50] + "..."
                self.alert("ERROR", f"Error in processing msg (catched): {error_msg}")
                return {"type": None}

    def auth(self):
        test_data = str(time.time()).encode()
        real_ans = sha256(test_data).hexdigest()
        self.send({"type": "auth", "test": test_data})
        ans = self.recv()["ans"]

        if real_ans == ans:
            self.alert("INFO", "Authenticated")
        else:
            self.alert("ERROR", "Authentication failed")
            self.conn.close()
            self.active = False

    def alert(self, type, msg):
        color = Fore.WHITE
        if type == "INFO":
            color = Fore.CYAN
        elif type == "WARNING":
            color = Fore.YELLOW
        elif type == "ERROR":
            color = Fore.RED
        print(color + f"[{self.addr}] " + msg + Fore.WHITE)

    def send(self, obj):
        data = pickle.dumps(obj)
        data = encrypt(data, ENCRYPT_OFFSET)
        len_msg = (str(len(data)) + self.padding)[:self.header].encode()

        packets = []
        while data:
            curr_len = min(len(data), self.packet_size)
            packets.append(data[:curr_len])
            data = data[curr_len:]

        self.conn.send(len_msg)
        for packet in packets:
            self.conn.send(packet)

    def recv(self):
        try:
            length = int(self.conn.recv(self.header))
            time.sleep(0.05)

            packet_sizes = [self.packet_size] * (length//self.packet_size)
            if (remain := (length % self.packet_size)) != 0:
                packet_sizes.append(remain)

            data = b""
            for size in packet_sizes:
                data += self.conn.recv(size)

            data = decrypt(data, ENCRYPT_OFFSET)
            return pickle.loads(data)

        except Exception as e:
            e = str(e)
            error_msg = e if len(e) < 50 else e[:50] + "..."
            print(Fore.RED + f"Error in recv (catched): {error_msg}" + Fore.WHITE)

            if self.raise_recv_error:
                raise Exception("Error in receive, server is still running.")

            return {"type": None}


def encrypt(msg, offset):
    msg = compress(msg)
    chars = [ch for ch in msg]
    chars = [ch+offset+i for i, ch in enumerate(chars)]
    chars = [ch % 256 for ch in chars]
    msg = bytes(chars)
    return msg


def decrypt(msg, offset):
    chars = [ch for ch in msg]
    chars = [ch-offset-i for i, ch in enumerate(chars)]
    chars = [ch % 256 for ch in chars]
    msg = bytes(chars)
    msg = decompress(msg)
    return msg
