import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from screenruler import RulerWindow

class SettingsWindow(QMainWindow):
    def __init__(self, ruler, *args, **kwargs):
        super(SettingsWindow, self).__init__(*args, **kwargs)

        self.ruler = ruler

        self.setWindowTitle("Screen Ruler")

        central_widget = CentralWidget()
        self.setCentralWidget(central_widget)

        greeting = QLabel("This is the options menu\nSet up your ruler for accurate measurements")
        font = greeting.font()
        font.setPointSize(13)
        greeting.setFont(font)
        central_widget.addWidget(greeting, 0, 0)

        input_widget = QWidget()
        input_layout = QGridLayout(input_widget)
        input_layout.setContentsMargins(0, 10, 0, 35)
        central_widget.addWidget(input_widget, 1, 0)

        texts = ["horizontal resolution: ", "vertical resolution: ", "screen diagonal size (in inches): "]
        for index, text in enumerate(texts):
            label = QLabel(text)
            input_layout.addWidget(label, index, 0)
    
        default_values = ["1920", "1080", "23"]
        fields = []
        for index, value in enumerate(default_values):
            input_field = QLineEdit(value)
            input_field.setMaximumSize(80, 20)
            fields.append(input_field)
            input_layout.addWidget(input_field, index, 1, Qt.AlignLeft)
        
        confirm_button = QPushButton("confirm")
        confirm_button.clicked.connect(lambda: self.start_ruler(fields))
        central_widget.addWidget(confirm_button, 3, 0, Qt.AlignCenter)

        a = QLabel("abc")
        a.show()

    def start_ruler(self, fields):
        h_res = fields[0].text()
        v_res = fields[1].text()
        size = fields[2].text()
        self.ruler.set_sizes(h_res, v_res, size)
        self.ruler.showFullScreen()
        self.hide()

class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(15, 10, 10, 10)
    
    def addWidget(self, widget, row, col, *args):
        self.layout.addWidget(widget, row, col, *args)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ruler = RulerWindow()
    window = SettingsWindow(ruler)

    window.show()

    app.exec_()