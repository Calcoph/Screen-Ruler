import math
import time

from PIL import ImageGrab, ImageStat

from PyQt5.QtCore import QLineF, QSize, Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

class Preview(QWidget):
    M_SIZE = (21, 21) # Siempre tienen que ser impares para que el cursor esté en el centro
    def __init__(self, h_res, v_res, *args, **kwargs):
        super(Preview, self).__init__(*args, **kwargs)
        
        self.h_res = h_res
        self.v_res = v_res

        self.xpadding = 150
        self.ypadding = 55
        self.grid_thickness = 1
        self.pixel_size = 7
        self.rect_width = self.M_SIZE[0]*self.pixel_size + self.grid_thickness*(self.M_SIZE[0]-1) + 1
        self.rect_height = self.M_SIZE[1]*self.pixel_size + self.grid_thickness*(self.M_SIZE[1]-1) + 1

        self.corner_positions = {
            1: (self.h_res-self.xpadding-self.rect_width, self.ypadding),
            2: (self.xpadding, self.ypadding),
            3: (self.xpadding, self.v_res-self.ypadding-self.rect_height),
            4: (self.h_res-self.xpadding-self.rect_width, self.v_res-self.ypadding-self.rect_height)
        }

        self.setFixedSize(QSize(self.rect_width+1, self.rect_height+1))
        self.update_pos()

    
    def update_pos(self):
        self.x, self.y = self.cursor().pos().x(), self.cursor().pos().y()
        self.true_corners = get_corners_coords(self.x, self.y, self.h_res, self.v_res, self.M_SIZE)
        self.screen_corners = get_corners_coords(self.x % self.h_res, self.y % self.v_res, self.h_res, self.v_res, self.M_SIZE)

    def paintEvent(self, event):
        if self.x >= self.h_res/2:
            if self.y >= self.v_res/2:
                cuadrant = 4
            else:
                cuadrant = 1
        else:
            if self.y >= self.v_res/2:
                cuadrant = 3
            else:
                cuadrant = 2
        
        opposite_cuadrants = {1: 3, 3: 1, 2: 4, 4: 2}
        cuadrant = opposite_cuadrants[cuadrant]
        corner = self.corner_positions[cuadrant]

        self.move(corner[0], corner[1])

        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor(75, 75, 75))

        # Paint border
        painter.drawRect(0, 0, self.rect_width, self.rect_height)

        # Paint the grid
        v_lines = []
        for i in range(self.M_SIZE[0]-1):
            x = 1+ (i+1) * self.pixel_size + self.grid_thickness * i
            line = QLineF(x, 1, x, self.rect_height - 1)
            v_lines.append(line)

        h_lines = []
        for i in range(self.M_SIZE[0]-1):
            y = 1 + (i+1) * self.pixel_size + self.grid_thickness * i
            line = QLineF(1, y, self.rect_width - 1, y)
            h_lines.append(line)

        painter.drawLines(v_lines)
        painter.drawLines(h_lines)

        # Paint zoomed pixels
        img = ImageGrab.grab(bbox=(self.true_corners[0][0],
                                      self.true_corners[0][1],
                                      self.true_corners[1][0],
                                      self.true_corners[1][1]),
                            all_screens=True)
        pixels = img.load()
        average = ImageStat.Stat(img).mean
        for row in range(self.M_SIZE[1]):
            for col in range(self.M_SIZE[0]):
                color = QColor(*pixels[col, row])
                
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawRect(1 + col * self.pixel_size + col * self.grid_thickness,
                                 1 + row * self.pixel_size + row * self.grid_thickness,
                                 self.pixel_size, self.pixel_size)

                if (row == self.y-self.true_corners[0][1]
                    or col == self.x-self.true_corners[0][0]):
                        pixel = ((255 - average[0]), (255 - average[1]), (255 - average[2]), 120)
                        color = QColor(*pixel)
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawRect(1 + col * self.pixel_size + col * self.grid_thickness,
                                 1 + row * self.pixel_size + row * self.grid_thickness,
                                 self.pixel_size, self.pixel_size)

def get_corners_coords(x, y, h_res, v_res, size):
    monitorx, monitory = 0, 0
    low_h, low_v, high_h, high_v = 0, 0, h_res, v_res
    temp_x = x
    while temp_x > h_res:
        temp_x -= h_res
        monitorx += 1
    high_h += monitorx * h_res
    low_h += monitorx * h_res
    temp_y = y
    while temp_y > v_res:
        temp_y -= v_res
        monitory += 1
    high_v += monitory * v_res
    low_v += monitory * v_res

    corners = [[0, 0], [h_res, v_res]]
    x_increment = (size[0] - 1)/2
    y_increment = (size[1] - 1)/2
    h_res -= 1
    v_res -= 1

    if x - x_increment > low_h:
        corners[0][0] = x - x_increment
        if x + x_increment < high_h:
            corners[1][0] = x + x_increment
        else:
            corners[1][0] = high_h
            corners[0][0] = high_h - size[0] + 1
    else:
        corners[0][0] = low_h
        corners[1][0] = low_h + size[0] - 1

    if y - y_increment > low_v:
        corners[0][1] = y - y_increment
        if y + y_increment < high_v:
            corners[1][1] = y + y_increment
        else:
            corners[1][1] = high_v
            corners[0][1] = high_v - size[1] + 1
    else:
        corners[0][1] = low_v
        corners[1][1] = low_v + size[1] - 1
    
    corners[1][0] += 1
    corners[1][1] += 1
    
    return corners