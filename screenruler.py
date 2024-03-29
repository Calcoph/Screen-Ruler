import sys
import math
import time

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QRect, QSize, Qt, QPoint
from PyQt5.QtGui import QBitmap, QCursor, QIcon, QPainter, QColor, QPixmap, QStaticText

from preview import Preview

# Subclass QMainWindow to customise your application's main window
class RulerWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(RulerWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Screen Ruler")
        self.setWindowIcon(QIcon("ruler.ico"))
        self.initial_dots = []
        self.final_dots = []

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ignored = False
        self.setMouseTracking(True)
        self.custom_cursor = self.generate_custom_cursor()
        #self.setCursor(Qt.BlankCursor)
        self.setCursor(self.custom_cursor)
    
    def set_sizes(self, h_res, v_res, size):
        if h_res == "auto":
            screen = self.screen()
            self.ppix = screen.physicalDotsPerInchX()
            self.ppiy = screen.physicalDotsPerInchY()
            h_res = screen.geometry().width()
            v_res = screen.geometry().height()
            #if self.ppix != self.ppiy:
            #    print("WARNING! due to the properties of your screen angles are slightly distorted and length of diagonals are approximations")
        else:
            diagonal_res = math.sqrt(int(h_res)**2+int(v_res)**2)
            self.ppix = diagonal_res/float(size) # Pixels per inch
            self.ppiy = self.ppix

        self.preview = Preview(h_res, v_res, self)
        self.preview.show()
        self.h_res, self.v_res = h_res, v_res
    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        if not self.ignored:
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

            if hipotenuse >= 20 and moving: # To not be in the way while looking for a second point
                painter.drawLine(top_horizontal_half, bot_horizontal_half)
                painter.drawLine(left_vertical_half, right_vertical_half)
                painter.drawLine(top_hipotenuse_half, bot_hipotenuse_half)

            painter.setPen(QColor(255, 255, 255))
            x_px = abs(int((halfx-i.x())*2)) + 1
            y_px = abs(int((halfy-mid_point.y())*2)) + 1
            hipotenuse = abs(hipotenuse)
            inch_to_cm = 2.54
            x_inches = x_px / self.ppix
            y_inches = y_px / self.ppiy
            hip_inches = hipotenuse / ((self.ppiy+self.ppix)/2)
            x_cm = x_inches * inch_to_cm
            y_cm = y_inches * inch_to_cm
            hip_cm = hip_inches * inch_to_cm
            x_text = str(x_px) + "px | " + f"{x_cm:7.2f}" + "cm | " + f"{x_inches:7.2f}" + "inch"
            y_text = str(y_px) + "px | " + f"{y_cm:7.2f}" + "cm | " + f"{y_inches:7.2f}" + "inch"
            hip_text = f"{abs(hipotenuse):7.2f}" + "px | " + f"{hip_cm:7.2f}" + "cm | " + f"{hip_inches:7.2f}" + "inch"
            # in 7.2f -> 7 = max char, 2 = max floating point precision
            if moving and hipotenuse >= 20: # To not be in the way while looking for a second point
                painter.drawText(QPoint(halfx, i.y()), x_text)
                painter.drawText(QPoint(end_point.x(), halfy), y_text)
                painter.drawText(QPoint(halfx, halfy-12), hip_text) # 7 = max char, 2 = max floating point precision
            elif not moving:
                # drawStaticText is more optimized if it rarely updates
                painter.drawStaticText(QPoint(halfx, i.y()), QStaticText(x_text))
                painter.drawStaticText(QPoint(end_point.x(), halfy), QStaticText(y_text))
                painter.drawStaticText(QPoint(halfx, halfy-12), QStaticText(hip_text))

        painter.setPen(QColor(255, 0, 255))
        for i in self.final_dots:
            painter.drawRect(i.x()-1, i.y()-1, 2, 2)

        """if not self.ignored:
            self.paint_cursor(painter)"""
        painter.end()
        
    def paint_background(self, painter):
        painter.setBrush(QColor(0, 0, 0, 120)) # Semitransparent brush
        painter.setPen(Qt.NoPen)
        corners = self.preview.screen_corners

        # drawRect(left margin, top margin, width, height)
        # corners[0] = top left corner
        # corners[1] = bot right corner
        # corners[][0] = x component
        # corners[][1] = y component

        # black rectangle
        # topleft corner =  (screen left, screen top)
        # botright corner = (preview left, screen bottom)
        painter.drawRect(0,
                         0,
                         corners[0][0],
                         self.v_res
        )
        # black rectangle
        # topleft corner =  (preview left, screen top)
        # botright corner = (preview right, preview top)
        painter.drawRect(corners[0][0],
                         0,
                         corners[1][0]-corners[0][0],
                         corners[0][1]
        )
        # black rectangle
        # topleft corner =  (preview left, preview bottom)
        # botright corner = (preview right, screen bottom)
        painter.drawRect(corners[0][0],
                         corners[1][1],
                         corners[1][0]-corners[0][0],
                         self.v_res - corners[1][1]
        )
        # black rectangle
        # topleft corner =  (preview right, screen top)
        # botright corner = (preview right, screen bot)
        painter.drawRect(corners[1][0],
                         0,
                         self.h_res - corners[1][0],
                         self.v_res
        )
        painter.setPen(QColor(255, 255, 255, 1)) # Almost transparent brush, just so there is something there
        painter.setBrush(QColor(0, 0, 0, 1)) # Almost transparent brush, just so there is something there
        # transparent rectangle with blue border
        # topleft corner =  (preview left, preview top)
        # botright corner = (preview right, preview bottom)
        painter.drawRect(corners[0][0]-1,
                         corners[0][1]-1,
                         corners[1][0]-corners[0][0]+1,
                         corners[1][1]-corners[0][1]+1
        )
        """painter.setBrush(QColor(255, 255, 255, 255))
        painter.drawRect(corners[0][0]+10, # 1 white dot where the cursor is
                         corners[0][1]+10,
                         1,
                         1
        )"""

    def mousePressEvent(self, event):
        if len(self.initial_dots) == len(self.final_dots):
            self.initial_dots.append(event.pos())
        else:
            self.final_dots.append(event.pos())
        self.repaint()
        self.preview.update()

    def mouseDoubleClickEvent(self, event):
        self.final_dots = []
        self.initial_dots = []
        self.update()
        self.preview.update()

    def mouseMoveEvent(self, event):
        self.preview.update_pos()
        self.repaint()
        self.preview.update()
            
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
        self.preview.repaint()

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
            self.preview.hide()
        else:
            self.preview.show()
            cursor = Qt.BlankCursor
        self.setCursor(cursor)

    def generate_custom_cursor(self):
        print(QPixmap.defaultDepth())
        bitmap = QPixmap(QSize(32, 32))
        mask = QPixmap(QSize(32, 32))
        bitmap.fill(QColor("#ffffff"))
        mask.fill(QColor("#ffffff"))

        x, y = Preview.M_SIZE
        painter = QPainter(bitmap)
        painter.setPen(QColor("#000000"))
        painter.drawRect(0, 0, x+2, y+2)
        painter.drawLine(x/2+2, 1, x/2+2, y+1)
        painter.drawLine(1, y/2+2, x+1, y/2+2)
        painter.end()

        return QCursor(QBitmap(bitmap), QBitmap(mask),(x+2)/2, (y+2)/2)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RulerWindow()

    # Qt.WindowTransparentForInput
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.setWindowOpacity(0.1)
    window.showFullScreen()

    app.exec_()