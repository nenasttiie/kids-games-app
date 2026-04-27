import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, \
    QHBoxLayout, QPushButton, QLineEdit, QDialog, QDialogButtonBox

from game import Game, GameStatus
from vector import Vector

class MainWindow(QWidget):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Game 2048")
        self._apply_shared_geometry()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowIcon(QIcon('rabbit.ico'))

        self.table = QTableWidget()
        self.table.setRowCount(game.size)
        self.table.setColumnCount(game.size)

        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(True)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QTableWidget.NoSelection)

        cell_size = 80
        for i in range(game.size):
            self.table.setColumnWidth(i, cell_size)
            self.table.setRowHeight(i, cell_size)

        table_size = game.size * (cell_size + 1)
        self.table.setFixedSize(table_size, table_size)

        layout = QVBoxLayout()
        self.label = QLabel("Нажмите стрелку ↑ ↓ ← →", self)
        self.label.setFont(QFont('Georgia', 14))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        layout_h_box = QHBoxLayout()
        self.button_settings = QPushButton('Настройки')
        self.button_settings.setFont(QFont('Georgia', 10))
        self.button_settings.setFixedWidth(120)
        self.button_settings.clicked.connect(self.show_settings)
        layout_h_box.addWidget(self.button_settings)
        layout_h_box.addStretch()

        self.label_points = QLabel(f"Счет: {self.game.points}")
        self.label_points.setFont(QFont('Georgia', 10))
        self.label_points.setAlignment(Qt.AlignRight)
        layout_h_box.addWidget(self.label_points)

        layout.addLayout(layout_h_box)
        layout.addStretch()
        layout.addWidget(self.table, 0, Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)
        self.update_table()

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        dialog.setWindowIcon(QIcon('rabbit.ico'))

        layout = QVBoxLayout(dialog)

        input_layout = QHBoxLayout()
        label = QLabel("Размер поля, n = ")
        self.label.setFont(QFont('Georgia', 11))
        input_layout.addWidget(label)

        self.input_text = QLineEdit()
        self.input_text.setText(str(self.game.size))
        input_layout.addWidget(self.input_text)

        layout.addLayout(input_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            try:
                new_size = int(self.input_text.text())
                print(new_size)
                cell_size = 80
                if new_size > 0:
                    self.table.setRowCount(new_size)
                    self.table.setColumnCount(new_size)

                    for i in range(new_size):
                        self.table.setColumnWidth(i, cell_size)
                        self.table.setRowHeight(i, cell_size)

                    table_size = new_size * (cell_size + 1)

                    self.table.setFixedSize(table_size, table_size)
                    self.new_game(new_size)
                    self.table.update()
            except ValueError:
                pass


    def show_lose_messagebox(self):
        msg = QMessageBox()
        custom_icon = QIcon('ch.ico')
        msg.setIconPixmap(custom_icon.pixmap(64, 64))
        msg.setWindowIcon(QIcon('rabbit.ico'))
        msg.setText("ПРОИГРЫШ (((")
        msg.setWindowTitle("2048")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        if retval == QMessageBox.Ok:
            self.new_game(self.game.size)

    def show_win_messagebox(self):
        msg = QMessageBox()
        custom_icon = QIcon('../../tp/kids game folder/kids-games-app/modules/2048/big.ico')
        msg.setIconPixmap(custom_icon.pixmap(64, 64))
        msg.setWindowIcon(QIcon('rabbit.ico'))
        msg.setText("ПОБЕДА! УРА!")
        msg.setWindowTitle("2048!!!!!")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        if retval == QMessageBox.Ok:
            self.new_game(self.game.size)

    def update_table(self):
        for i in range(self.game.size):
            for j in range(self.game.size):
                value = self.game.matrix[i][j]
                item = QTableWidgetItem(str(value) if value != 0 else "")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        self.label_points.setText(f"Счет: {self.game.points}")

    def new_game(self, size):
        self.game = Game(size)
        self.update_table()

    def keyPressEvent(self, event):
        direction_map = {
            Qt.Key_Up: Vector(-1,0),
            Qt.Key_Down: Vector(1, 0),
            Qt.Key_Right: Vector(0, 1),
            Qt.Key_Left: Vector(0, -1)
        }

        if event.key() in direction_map:
            self.game.shift(direction_map[event.key()])
            # self.label_points.setText(f"Счет: {self.game.points}")
            self.update_table()
            if self.game.status == GameStatus.WIN:
                self.show_win_messagebox()
            if self.game.status == GameStatus.LOSE:
                self.show_lose_messagebox()

    def _apply_shared_geometry(self):
        x = os.getenv("APP_WINDOW_X")
        y = os.getenv("APP_WINDOW_Y")
        w = os.getenv("APP_WINDOW_W")
        h = os.getenv("APP_WINDOW_H")

        if x and y and w and h:
            try:
                self.setGeometry(int(x), int(y), int(w), int(h))
                return
            except ValueError:
                pass




if __name__ == '__main__':
    app = QApplication(sys.argv)
    g = Game(4)
    window = MainWindow(g)
    window.show()
    sys.exit(app.exec_())