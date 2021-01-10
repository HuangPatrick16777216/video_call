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

import threading
import pygame
from _constants import *
from _elements import Button, Text, TextInput


class Waiting:
    def __init__(self):
        self.text_header = Text(FONT_LARGE.render("Meeting", 1, BLACK))
        self.text_attendees = Text(FONT_MED.render("Attendees", 1, BLACK))
        self.text_info = Text(FONT_MED.render("Info", 1, BLACK))

    def draw(self, window, events, conn):
        width, height = window.get_size()

        window.fill(WHITE)
        self.text_header.draw(window, (width//2, 50))
        self.text_attendees.draw(window, (width//3, 100))
        self.text_info.draw(window, (width//1.5, 100))