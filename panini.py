#!/usr/bin/env python

# Copyright (c) 2023 Nikos Skalkotos <skalkoto@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys
import os.path
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton,
                             QHBoxLayout, QStatusBar, QMessageBox)

SUPERSCRIPT = {
    0: '\u2070',
    1: '\u00b9',
    2: '\u00b2',
    3: '\u00b3',
    4: '\u2074',
    5: '\u2075',
    6: '\u2076',
    7: '\u2077',
    8: '\u2078',
    9: '\u2079',
}

CONFIG_FILE = "{}{}.panini.json".format(os.path.expanduser('~'), os.sep)


def toSuperscript(num):
    digits = []
    while num > 0:
        digit = num % 10
        digits.append(SUPERSCRIPT[digit])
        num = num // 10
    digits.reverse()
    return "".join(digits)


class Panini(QWidget):
    def __init__(self):
        super().__init__()
        self.values = {}
        for i in range(441):
            self.values[str(i + 1)] = 0

        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        for i in range(21):
            for j in range(21):
                name = str(i * 21 + j + 1)
                button = QPushButton(self)
                button.setProperty("name", name)
                self.decorateButton(button, self.values[name])
                button.setFixedSize(35, 20)
                button.clicked.connect(
                    lambda state, button=button: self.buttonClicked(button))
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(
                    lambda pos, button=button: self.contextMenuEvent(
                        pos, button))
                grid.addWidget(button, i, j)

        hbox1 = QHBoxLayout()
        self.saveButton = QPushButton('Save', self)
        self.saveButton.clicked.connect(self.save)
        hbox1.addWidget(self.saveButton)
        self.loadButton = QPushButton('Load', self)
        self.loadButton.clicked.connect(self.load)
        hbox1.addWidget(self.loadButton)
        hbox1.addStretch(1)
        grid.addLayout(hbox1, 21, 0, 1, 21)

        hbox2 = QHBoxLayout()
        self.statusBar = QStatusBar()
        hbox2.addWidget(self.statusBar)
        grid.addLayout(hbox2, 22, 0, 1, 21)

        self.updateStatusBar()

        self.setWindowTitle('Panini FIFA 365 2023')

        if os.path.isfile(CONFIG_FILE):
            self.load()
        else:
            self.loadButton.setEnabled(False)

        self.show()

    def computeStatistics(self):
        missing = len([v for v in self.values if not self.values[v]])
        double = sum([v - 1 for v in self.values.values() if v > 1])

        return f"missing: {missing}, double: {double}"

    def updateStatusBar(self):
        self.statusBar.showMessage(self.computeStatistics())

    def decorateButton(self, button, value):
        if value == 0:
            color = "white"
        if value == 1:
            color = "green"
        if value > 1:
            color = "yellow"

        button.setStyleSheet(f'background-color: {color};')

        text = button.property("name")
        if value > 2:
            text += toSuperscript(value - 1)
        button.setText(text)

    def buttonClicked(self, button):
        name = button.property("name")
        self.values[name] += 1
        self.decorateButton(button, self.values[name])
        self.updateStatusBar()

    def contextMenuEvent(self, event, button):
        name = button.property("name")
        if self.values[name] > 0:
            self.values[name] -= 1
        self.decorateButton(button, self.values[name])
        self.updateStatusBar()

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            f.write(json.dumps(self.values))

        self.loadButton.setEnabled(True)

    def load(self):
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.values = json.load(f)
                for index in self.values:
                    i = (int(index) - 1) // 21
                    j = (int(index) - 1) % 21
                    button = self.layout().itemAtPosition(i, j).widget()
                    assert (button.property("name") == index)
                    value = self.values[index]
                    self.decorateButton(button, value)

            self.updateStatusBar()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("No config to load from")
            msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    panini = Panini()
    sys.exit(app.exec_())
