import pygame
from pygame.locals import *

width, height = 750, 600
# Window
pygame.init()
window = pygame.display.set_mode((width, height), HWSURFACE | DOUBLEBUF | RESIZABLE)

hfield_width = 52.5
hfield_heigh = 35.0


class FieldDisplay(object):
    """
    Draw a soccer field for testings.
    """

    def __init__(self):
        pass


    @staticmethod
    def _convert_coordinates(x, y):
        """
        Convert to field coordinates.
        :param x:
        :param y:
        :return:
        """
        scale = 6.0
        # center of the field
        cx, cy = hfield_width * scale, hfield_heigh * scale
        mx, my = 30 + cx, 20 + cy

        x, y = mx + scale * x, my + scale * y
        return x, y


    def clear(self):
        """
        Clear the window  with an empty field.
        """
        # Draw the canvas
        window.fill((255, 255, 255))

        ox, oy = self._convert_coordinates(-hfield_width, -hfield_heigh)
        fx, fy = self._convert_coordinates(hfield_width, hfield_heigh)
        pygame.draw.rect(window, (55, 171, 84), (ox, oy, fx - ox, fy - oy))
        pygame.draw.rect(window, (0, 0, 0), (ox, oy, fx - ox, fy - oy), 2)

        self.draw_circle([0, 0], 30, color=(0, 0, 0), stroke=2)
        self.draw_line([0, -hfield_heigh], [0, hfield_heigh])


    def draw_circle(self, center, radio, color=(200, 0, 0), stroke=0):
        """
        Draw a circle
        :param center:
        :param radio:
        :param color:
        :param stroke:
        """
        center = self._convert_coordinates(center[0], center[1])
        pygame.draw.circle(window, color, (int(center[0]), int(center[1])), int(radio), stroke)

    def draw_line(self, p1, p2, color=(0, 0, 0), stroke=2):
        """
        Draw a line
        :param p1:
        :param p2:
        :param color:
        :param stroke:
        """
        p1 = self._convert_coordinates(*p1)
        p2 = self._convert_coordinates(*p2)

        pygame.draw.line(window, color,
                         p1,
                         p2, stroke)


    def show(self):
        """
        Show the drawings.
        """
        pygame.display.flip()


## For testing this class
if __name__ == "__main__":
    import time

    display = FieldDisplay()


    for i in range(30):
        display.clear()
        display.draw_circle([i, 0], 10)
        display.show()
        time.sleep(0.1)
