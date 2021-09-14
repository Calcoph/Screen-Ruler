import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QLineEdit, QPushButton, QCheckBox
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon

from screenruler import RulerWindow

class SettingsWindow(QMainWindow):
    def __init__(self, ruler, *args, **kwargs):
        super(SettingsWindow, self).__init__(*args, **kwargs)

        self.ruler = ruler

        self.setWindowTitle("Screen Ruler")
        app_icon = QIcon("ruler.ico")
        self.setWindowIcon(app_icon)

        central_widget = CentralWidget()
        self.setCentralWidget(central_widget)

        greeting = QLabel("This is the options menu\nSet up your ruler for accurate measurements")
        font = greeting.font()
        font.setPointSize(13)
        greeting.setFont(font)
        central_widget.addWidget(greeting, 0, 0)

        auto_widget = QWidget()
        auto_layout = QGridLayout(auto_widget)
        auto_label = QLabel("Auto")
        self.auto_checkbox = QCheckBox()
        self.auto_checkbox.clicked.connect(self.toggle_auto)
        auto_layout.addWidget(auto_label, 0, 0, Qt.AlignRight)
        auto_layout.addWidget(self.auto_checkbox, 0, 1)
        central_widget.addWidget(auto_widget, 1, 0)

        input_widget = QWidget()
        self.input_layout = QGridLayout(input_widget)
        self.input_layout.setContentsMargins(0, 10, 0, 35)
        central_widget.addWidget(input_widget, 2, 0)

        texts = ["horizontal resolution: ", "vertical resolution: ", "screen diagonal size (in inches): "]
        for index, text in enumerate(texts):
            label = QLabel(text)
            self.input_layout.addWidget(label, index, 0)
    
        default_values = ["1920", "1080", "23"]
        fields = []
        for index, value in enumerate(default_values):
            input_field = QLineEdit(value)
            input_field.setStyleSheet("QLineEdit:read-only { background: darkgray; selection-background-color: gray; border: darkgray; }")
            input_field.setMaximumSize(80, 20)
            fields.append(input_field)
            self.input_layout.addWidget(input_field, index, 1, Qt.AlignLeft)
        
        confirm_button = QPushButton("confirm")
        confirm_button.clicked.connect(lambda: self.start_ruler(fields))
        central_widget.addWidget(confirm_button, 3, 0, Qt.AlignCenter)

        self.auto_checkbox.click()

    def start_ruler(self, fields):
        if self.auto_checkbox.isChecked():
            h_res = "auto"
            v_res = "auto"
            size = "auto"
        else:
            h_res = fields[0].text()
            v_res = fields[1].text()
            size = fields[2].text()
        self.ruler.set_sizes(h_res, v_res, size)
        self.ruler.showFullScreen()
        self.hide()

    def toggle_auto(self, state):
        for i in range(6):
            widget = self.input_layout.itemAt(i).widget()
            if type(widget) == QLineEdit:
                widget.setReadOnly(state)

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