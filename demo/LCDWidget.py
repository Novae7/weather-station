#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Starter Kit: Weather Station Demo Application(Brick Viewer) 
Copyright (C) 2013 Bastian Nordmeyer <bastian@tinkerforge.com>

LCDWidget.py: LCD Display Widget Implementation which controls
also physical LCD20x4 Bricklet

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation; either version 2 
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QFont
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal, SIGNAL, SLOT
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QWidget
from tinkerforge.bricklet_lcd_20x4 import LCD20x4


import math


class LCDChar (QLabel):

    qtcb_set_char = pyqtSignal(str)

    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        
        font = QFont()
        font.setPixelSize(self.height())
        self.setFont(font)
        self.qtcb_set_char.connect(self.set_char_slot)

        self.setText(" ")


        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.blue)
        palette.setColor(self.foregroundRole(), Qt.white)
        self.setPalette(palette)

    def set_char_slot(self, char):

        if char == '\xDF':
            char = '\xB0'
        self.setText(char)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def set_char(self, char):
        self.qtcb_set_char.emit(char)


class LCDWidget (QWidget):

    qtcb_write_line = pyqtSignal(int, int, str)

    def __init__(self, parent, app):
        super(QWidget, self).__init__(parent)
        self.array = [[None for x in range(20)] for y in range(4)]
        self.grid = None

        self.app = app

        self.setFixedSize(550, 200)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        palette.setColor(self.foregroundRole(), Qt.white)
        self.setPalette(palette)


        self.qtcb_write_line.connect(self.write_line_slot)
        self.configure_custom_chars()

        self.grid = QGridLayout()

        for y in range(len(self.array)):
            for x in range(len(self.array[0])):
                character = LCDChar(self)
                self.array[y][x] = character
                self.grid.addWidget(character,y,x)

        self.setLayout(self.grid)

    def configure_custom_chars(self):
        c = [[0x00 for x in range(8)] for y in range(8)]
	
		c[0] = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff]
		c[1] = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff]
		c[2] = [0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff]
		c[3] = [0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff]
		c[4] = [0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff]
		c[5] = [0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
		c[6] = [0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
		c[7] = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]

		for i in range(self.Length):
			self.app.lcd.set_custom_character(i, c[i]);

    def write_line_slot(self, line, begin, text):

        if self.app.lcd is not None:
            self.app.lcd.write_line(line, begin, str(text.toAscii().data()))

        for i in range(len(self.array[0])):
            try:
                self.array[line][i].set_char(text[i])
            except Exception:
                break

    def write_line(self, line, begin, text):
        self.qtcb_write_line.emit(line, begin, text)

    def clear(self):
        self.write_line(0,0, "                    ")
        self.write_line(1,0, "                    ")
        self.write_line(2,0, "                    ")
        self.write_line(3,0, "                    ")
