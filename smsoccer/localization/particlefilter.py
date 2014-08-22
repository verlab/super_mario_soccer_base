import math

__author__ = 'dav'
import numpy as np

# Number of particles
N = 10


def _update_estimated_position():
    pass


class ParticleFilter(object):
    def __init__(self, initial_position):
        """

        :param initial_position: [x, y, theta]
        """
        self.particles = np.array([initial_position[:] for i in range(N)])

        # Estimated position
        self.e_position = initial_position[:]


    def dash_particles(self, dash):
        """
        Move the particles forward
        :param dash: (vel_lin, vel_ang)
        """
        theta = self.e_position[2]
        c = 0.01  # convert dash to velocity
        dx = dash * c * math.cos(math.radians(theta))
        dy = dash * c * math.sin(math.radians(theta))

        varx = 0.1
        vary = 0.1

        # random movement
        rdx = varx * np.random.randn(N) + dx
        rdy = vary * np.random.randn(N) + dy

        #movement in x,y
        mov = np.vstack((rdx, rdy))
        #movement with theta=0
        mov = np.vstack((mov, np.zeros(N)))

        print mov
        self.particles = self.particles + mov.T

        self._update_estimated_position()

    def rotate_particles(self, angle):
        """
        Rotate all the particles, it does not have uncertainty.
        :param angle: rotation angle
        """
        self.particles[:, 2] += angle
        self._update_estimated_position()


    def _update_estimated_position(self):
        self.e_position = np.mean(self.particles, axis=0)


if __name__ == "__main__":
    pf = ParticleFilter((5, 10, 0))
    print pf.particles

    # dash
    pf.dash_particles(10)
    print pf.particles, pf.e_position

    #rotate
    pf.rotate_particles(30)
    print pf.particles, pf.e_position







