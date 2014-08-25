import pygame
from pygame.locals import *

from smsoccer.world.game_object import Flag


MARGIN_UP = 50
MARGIN_LEFT = 70

width, height = 800, 600
# Window
pygame.init()
window = pygame.display.set_mode((width, height), HWSURFACE | DOUBLEBUF | RESIZABLE)

SCALE = 6.0

# left top
ltx, lty = Flag.FLAG_COORDS["lt"]
# right bottom
rbx, rby = Flag.FLAG_COORDS["rb"]

hfield_width = (rbx - ltx) / 2.0
hfield_heigh = (rby - lty) / 2.0


class FieldDisplay(object):
    """
    Draw a soccer field for testings.
    """

    def __init__(self, show_flags=False):
        self.show_flags = show_flags


    @staticmethod
    def _convert_coordinates(x, y):
        """
        Convert to field coordinates.
        :param x:
        :param y:
        :return:
        """

        # center of the field
        cx, cy = hfield_width * SCALE, hfield_heigh * SCALE
        mx, my = MARGIN_LEFT + cx, MARGIN_UP + cy

        x, y = mx + SCALE * x, my + SCALE * y
        return x, y


    def clear(self):
        """
        Clear the window  with an empty field.
        """
        # Draw the canvas
        window.fill((255, 255, 255))
        # grass
        self.draw_rect((ltx, lty), rbx - ltx, rby - lty, (55, 171, 84))
        # border
        self.draw_rect((ltx, lty), rbx - ltx, rby - lty, (0, 0, 0), 1)
        # Center
        self.draw_circle([0, 0], 30, color=(0, 0, 0), stroke=2)

        self.draw_line([0, lty], [0, rby])

        # Area left
        plt_x, plt_y = Flag.FLAG_COORDS["plt"]
        self.draw_rect([ltx, plt_y], rbx - ltx, rby - lty, (0, 0, 0), 1)


        self.draw_line([ltx, plt_y], [plt_x, plt_y])
        plb_x, plb_y = Flag.FLAG_COORDS["plb"]
        self.draw_line([plt_x, plt_y], [plb_x, plb_y])
        self.draw_line([ltx, plb_y], [plt_x, plb_y])

        # Area
        prt_x, prt_y = Flag.FLAG_COORDS["prt"]
        self.draw_line([rbx, prt_y], [prt_x, prt_y])
        prb_x, prb_y = Flag.FLAG_COORDS["prb"]
        self.draw_line([prt_x, prt_y], [prb_x, prb_y])
        self.draw_line([rbx, prb_y], [prt_x, prb_y])


        # Show flags
        if self.show_flags:
            for flag, p in Flag.FLAG_COORDS.items():
                self.draw_circle(p, 3)
                self.draw_text(p, flag)


    def draw_rect(self, point, width, heigh, color=(0, 0, 0), stroke=0):
        point = self._convert_coordinates(*point)
        pygame.draw.rect(window, color, (point[0], point[1], SCALE * width, SCALE * heigh), stroke)

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

    def draw_text(self, point, text, color=(0, 0, 0)):
        point = self._convert_coordinates(*point)
        font = pygame.font.Font(None, 30)
        label = font.render(str(text), 1, color)
        window.blit(label, point)


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
        p = [i, 0]
        display.draw_circle(p, 10)
        display.draw_text(p, str(i))
        display.show()
        time.sleep(1.1)

