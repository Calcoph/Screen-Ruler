from PyQt5.QtWidgets import QLayout
from PyQt5.QtCore import QSize, QRect

class SmartGridItem():
    def __init__(self, widget, left=0, top=0, right=0, bot=0):
        self.padding = (left, top, right, bot)
        self.widget = widget

class SmartGridLayout(QLayout):
    def __init__(self, parent, shape):
        super().__init__(parent)

        self.shape = shape
        self.setGeometry(QRect(0, 0, 0, 0))

    def setGeometry(self, rect):
        if len(self.shape) == 0:
            return

        self.x_position = rect.x()
        self.lowest_point = rect.y()
        new_lowest_point = 0
        for i in self.shape:
            for j in i:
                if type(j) != SmartGridItem:
                    padding = (0, 0, 0, 0)
                    widget = j
                else:
                    padding = j.padding
                    widget = j.widget

                widget.setGeometry(self.x_position + padding[0], self.lowest_point + padding[1], widget.width(), widget.height())

                if new_lowest_point < self.lowest_point + padding[1] + widget.height():
                    new_lowest_point = self.lowest_point + padding[1] + widget.height()
                self.x_position += padding[0] + widget.width()
            if new_lowest_point > self.lowest_point:
                self.lowest_point = new_lowest_point
    
    def sizeHint(self):
        return QSize(self.x_position, self.lowest_point)
    
    def minimumSize(self):
        return QSize(self.x_position, self.lowest_point)