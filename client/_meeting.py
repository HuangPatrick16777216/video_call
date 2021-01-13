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
from _constants import *
from _elements import Button, Text, TextInput, Scrollable


class Meeting:
    def __init__(self, conn):
        self.conn = conn

        self.video = False
        self.button_video_on = Button(FONT_MED.render("Video ON", 1, BLACK))
        self.button_video_off = Button(FONT_MED.render("Video OFF", 1, BLACK))

    def draw(self, window, events):
        width, height = window.get_size()

        window.fill(WHITE)

        if self.video:
            if self.button_video_off.draw(window, events, (20, height-70), (200, 50)):
                self.video = False
        else:
            if self.button_video_on.draw(window, events, (20, height-70), (200, 50)):
                self.video = True
