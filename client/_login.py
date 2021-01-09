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

import pygame
from _constants import *
from _elements import Button, Text


class Login:
    def __init__(self):
        self.status = "CHOOSE"
        self.text_header = Text(FONT_LARGE.render("Video Call", 1, BLACK))
        self.button_join = Button(FONT_MED.render("Join a meeting", 1, BLACK))
        self.button_create = Button(FONT_MED.render("Create a meeting", 1, BLACK))

    def draw(self, window, events):
        width, height = window.get_size()

        window.fill(WHITE)
        self.text_header.draw(window, (width//2, height//2-100))

        if self.status == "CHOOSE":
            self.button_join.draw(window, events, (width//2, height//2), (300, 50))
            self.button_create.draw(window, events, (width//2, height//2+75), (300, 50))
