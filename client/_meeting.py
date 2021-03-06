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
import threading
import pygame
import cv2
from _constants import *
from _elements import Button, Text, TextInput, Scrollable


class Meeting:
    def __init__(self, conn):
        self.conn = conn

        self.active = True
        self.threads_started = False
        self.attendees = []
        self.videos = []

        self.find_video_size()

        self.video_on = False
        self.video_curr = pygame.image.tostring(pygame.Surface(self.video_res), "RGB")
        self.button_video_on = Button(FONT_SMALL.render("Turn video on", 1, BLACK))
        self.button_video_off = Button(FONT_SMALL.render("Turn video off", 1, BLACK))

    def find_video_size(self):
        image = cv2.VideoCapture(0).read()[1]
        height, width = image.shape[:2]

        width_fac = width/480
        height_fac = height/270

        if width_fac > height_fac:
            self.video_res = (int(width/width_fac), int(height/width_fac))
        else:
            self.video_res = (int(width/height_fac), int(height/height_fac))

    def get_info(self):
        while self.active:
            try:
                self.conn.send({"type": "meeting_get"})
                self.attendees = self.conn.recv()["data"]
                self.videos = self.conn.recv()["data"]

                send_data = {
                    "type": "meeting_get",
                    "video_on": self.video_on,
                    "video": (self.video_curr, self.video_res),
                    "audio_on": False,
                    "audio": None
                }
                self.conn.send(send_data)

            except KeyError:
                continue

    def update_video(self):
        capturer = cv2.VideoCapture(0)

        while self.active:
            if self.video_on:
                image = capturer.read()[1]
                image = cv2.resize(image, self.video_res)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                surface = pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")
                self.video_curr = pygame.image.tostring(surface, "RGB")

            time.sleep(0.01)

    def draw(self, window, events):
        if not self.threads_started:
            threading.Thread(target=self.get_info).start()
            threading.Thread(target=self.update_video).start()
            self.threads_started = True

        width, height = window.get_size()

        window.fill(WHITE)

        x_loc = 0
        for img, res in self.videos:
            if img is not None:
                surface = pygame.image.fromstring(img, res, "RGB")
                window.blit(surface, (x_loc, 0))
                x_loc += window.get_width()

        if self.video_on:
            if self.button_video_off.draw(window, events, (80, height-50), (120, 30)):
                self.video_on = False
        else:
            self.video_curr = pygame.image.tostring(pygame.Surface(self.video_res), "RGB")
            if self.button_video_on.draw(window, events, (80, height-50), (120, 30)):
                self.video_on = True
