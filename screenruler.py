import sys
import math

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QGridLayout
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QFont, QPaintDevice, QPainter, QColor, QStaticText, QMouseEvent

# Subclass QMainWindow to customise your application's main window
class RulerWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(RulerWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Screen Ruler")
        self.initial_dots = []
        self.final_dots = []

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ignored = False
        self.setMouseTracking(True)
        self.setCursor(Qt.BlankCursor)
    
    def set_sizes(self, h_res, v_res, size):
        diagonal_res = math.sqrt(int(h_res)**2+int(v_res)**2)
        self.ppi = diagonal_res/float(size) # Pixels per inch
    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.paint_background(painter)
        painter.setPen(QColor(255, 0, 255))
        painter.setBrush(QColor(0, 0, 0))

        for index, i in enumerate(self.initial_dots):
            painter.setPen(QColor(255, 0, 255))
            painter.drawRect(i.x()-1, i.y()-1, 2, 2)
            try:
                end_point = self.final_dots[index]
                painter.setPen(QColor(0, 0, 255))
                moving = False
            except IndexError:
                # There is no end point, so cursor is end point
                end_point = self.cursor().pos()
                painter.setPen(QColor(0, 0, 255, 64))
                moving = True

            mid_point = QPoint(end_point.x(), i.y())
            painter.drawPolyline(i, mid_point, end_point, i)
            painter.setPen(QColor(255, 0, 255))
            halfx = (mid_point.x() - i.x())/2+i.x()
            halfy = (end_point.y() - mid_point.y())/2+mid_point.y()

            # Draw perpendicular magenta lines in each of the triangle's sides' center
            top_horizontal_half = QPoint(halfx, i.y()+10)
            bot_horizontal_half = QPoint(halfx, i.y()-10)

            left_vertical_half = QPoint(end_point.x()-10, halfy)
            right_vertical_half = QPoint(end_point.x()+10, halfy)
            try:
                hipotenuse = math.sqrt((2*(halfx-i.x()))**2+(2*(halfy-mid_point.y()))**2)
                scaling_factor = hipotenuse/10 # To ensure line length = 10
                y_change = (2*(halfx-i.x()) / scaling_factor)
                x_change = (2*(halfy-mid_point.y()) / scaling_factor)

            except ZeroDivisionError:
                y_change = 0
                x_change = 0

            top_hipotenuse_half = QPoint(halfx-x_change, halfy+y_change)
            bot_hipotenuse_half = QPoint(halfx+x_change, halfy-y_change)

            painter.drawLine(top_horizontal_half, bot_horizontal_half)
            painter.drawLine(left_vertical_half, right_vertical_half)
            painter.drawLine(top_hipotenuse_half, bot_hipotenuse_half)

            painter.setPen(QColor(255, 255, 255))
            x_px = abs(int((halfx-i.x())*2))
            y_px = abs(int((halfy-mid_point.y())*2))
            hipotenuse = abs(hipotenuse)
            inch_to_cm = 2.54
            x_inches = x_px / self.ppi
            y_inches = y_px / self.ppi
            hip_inches = hipotenuse / self.ppi
            x_cm = x_inches * inch_to_cm
            y_cm = y_inches * inch_to_cm
            hip_cm = hip_inches * inch_to_cm
            x_text = str(x_px) + "px | " + f"{x_cm:7.2f}" + "cm | " + f"{x_inches:7.2f}" + "inch"
            y_text = str(y_px) + "px | " + f"{y_cm:7.2f}" + "cm | " + f"{y_inches:7.2f}" + "inch"
            hip_text = f"{abs(hipotenuse):7.2f}" + "px | " + f"{hip_cm:7.2f}" + "cm | " + f"{hip_inches:7.2f}" + "inch"
            # in 7.2f -> 7 = max char, 2 = max floating point precision
            if moving:
                painter.drawText(QPoint(halfx, i.y()), x_text)
                painter.drawText(QPoint(end_point.x(), halfy), y_text)
                painter.drawText(QPoint(halfx, halfy-12), hip_text) # 7 = max char, 2 = max floating point precision
            else:
                # drawStaticText is more optimized if it rarely updates
                painter.drawStaticText(QPoint(halfx, i.y()), QStaticText(x_text))
                painter.drawStaticText(QPoint(end_point.x(), halfy), QStaticText(y_text))
                painter.drawStaticText(QPoint(halfx, halfy-12), QStaticText(hip_text))

        painter.setPen(QColor(255, 0, 255))
        for i in self.final_dots:
            painter.drawRect(i.x()-1, i.y()-1, 2, 2)

        if not self.ignored:
            self.paint_cursor(painter)
        painter.end()
        
    def paint_background(self, painter):
        painter.setBrush(QColor(0, 0, 0, 35)) # Semitransparent brush
        painter.drawRect(0, 0, 1920, 1080)
    
    def paint_cursor(self, painter, length=10):
        painter.setPen(QColor(255, 255, 255)) # It mustn't be monochrome so subpixels don't mess precision up
        x, y = self.cursor().pos().x(), self.cursor().pos().y()
        top_dot = QPoint(x, y+length)
        bot_dot = QPoint(x, y-length)
        left_dot = QPoint(x-length, y)
        right_dot = QPoint(x+length, y)
        painter.drawLine(top_dot, bot_dot)
        painter.drawLine(right_dot, left_dot)

    def mousePressEvent(self, event):
        if len(self.initial_dots) == len(self.final_dots):
            self.initial_dots.append(event.pos())
        else:
            self.final_dots.append(event.pos())
        self.repaint()

    def mouseDoubleClickEvent(self, event):
        self.final_dots = []
        self.initial_dots = []
        self.repaint()

    def mouseMoveEvent(self, event):
        self.repaint()
    
    def keyPressEvent(self, event):
        key = event.key()
        if key in [16777234, 16777235, 16777236, 16777237]: # Arrows
            cursor = self.cursor()
            x = cursor.pos().x()
            y = cursor.pos().y()
            if key == 16777234: # Left arrow
                new_x, new_y = (x-1, y) 
            if key == 16777235: # Up arrow
                new_x, new_y = (x, y-1)
            if key == 16777236: # Right arrow
                new_x, new_y = (x+1, y)
            if key == 16777237: # Down arrow
                new_x, new_y = (x, y+1)
            cursor.setPos(new_x, new_y)
        elif key == 80: # P key
            self.ignore_input(not self.ignored)
        elif key == 16777220: # Enter key
            # Simulate click
            self.mousePressEvent(self.cursor())

    def ignore_input(self, ignore=True):
        self.ignored = ignore
        self.setMouseTracking(not ignore)
        flags = Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint
        if ignore:
            flags = flags | Qt.WindowTransparentForInput
        self.setWindowFlags(flags)
        self.showFullScreen()
        if ignore:
            cursor = Qt.ArrowCursor
        else:
            cursor = Qt.BlankCursor
        self.setCursor(cursor)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RulerWindow()

    # Qt.WindowTransparentForInput
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.setWindowOpacity(0.1)
    window.showFullScreen()

    app.exec_()