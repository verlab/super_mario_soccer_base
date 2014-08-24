import math
from numpy.random import random

from smsoccer.localization.distributions import multivariate_normal


__author__ = 'dav'
import numpy as np

# Number of particles
N = 10

# Motion variance (theta is zero)
VAR_X = 3
VAR_Y = 0.0
VAR_T = 0.0

# Update variance: x, y, theta.
sigma = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.1]])


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
        #TODO compute c
        c = 0.01  # convert dash to velocity
        dx = dash * c * math.cos(math.radians(theta))
        dy = dash * c * math.sin(math.radians(theta))


        # random movement
        rdx = VAR_X * np.random.randn(N) + dx
        rdy = VAR_Y * np.random.randn(N) + dy
        rdth = VAR_T * np.random.randn(N) + theta

        #movement in x,y
        mov = np.vstack((rdx, rdy))
        #movement with theta=0
        mov = np.vstack((mov, rdth))

        self.particles = self.particles + mov.T

        self._update_estimated_position()

    def rotate_particles(self, angle):
        """
        Rotate all the particles, it does not have uncertainty.
        :param angle: rotation angle
        """
        self.particles[:, 2] += angle
        self._update_estimated_position()

    def resample(self, weights):

        indices = []
        c = [0.] + [sum(weights[:i + 1]) for i in range(N)]
        u0, j = random(), 0
        for u in [(u0 + i) / N for i in range(N)]:
            while u > c[j]:
                j += 1
            indices.append(j - 1)
        return indices


    def update_particles(self, perception):

        # Weights.
        w = []
        for x in self.particles:
            w1 = multivariate_normal(x, perception, sigma)
            w.append(w1)


        # normalize the weights.
        w = np.array(w) / sum(w)
        print w
        # Resample
        ids = self.resample(w)
        print ids
        self.particles = self.particles[ids]


    def _update_estimated_position(self):
        self.e_position = np.mean(self.particles, axis=0)


if __name__ == "__main__":
    pf = ParticleFilter([5, 10, 0])
    # print pf.particles

    # # dash
    pf.dash_particles(10)
    print pf.particles, pf.e_position
    #
    # #rotate
    # pf.rotate_particles(30)
    # print pf.particles, pf.e_position

    pf.update_particles([5, 10, 0])

    print pf.particles, pf.e_position






