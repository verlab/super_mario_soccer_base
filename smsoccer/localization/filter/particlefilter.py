from numpy.random import random

import numpy as np

from smsoccer.localization.filter.distributions import multivariate_normal

# Number of particles
N = 1500

# Motion variance, Linear and angular
VAR_L = 0.5
VAR_T = 15
# Variance in rotation
VAR_TURN = 22.0

# Update variance: x, y, theta.
# sigma = np.array([[15.0, 0.0, 0.0], [0.0, 15.0, 0.0], [0.0, 0.0, 10.0]])
sigma = np.array([[20.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 140.0]])

SHOW_PARTICLES = True


class ParticleFilter(object):
    def __init__(self):
        self.started = False

        x = -55 + np.random.randn(N) * 110
        y = -35 + np.random.randn(N) * 70
        th = -180 + np.random.randn(N) * 180

        xy = np.vstack((x, y))
        self.particles = np.vstack((xy, th)).T
        self._update_estimated_position()


    def start_position(self, initial_position):
        """

        :param initial_position: [x, y, theta]
        """
        self.particles = np.array([initial_position[:] for i in range(N)])

        # Estimated position
        self.e_position = initial_position[:]

        self.started = True

    def dash_particles(self, dash):
        """
        Move the particles forward
        :param dash: (vel_lin, vel_ang)
        """
        if dash > 100:
            dash = 100

        theta = self.particles[:, 2]
        # TODO compute c
        c = 3.0 / 100.0  # convert dash to velocity

        # displacement
        c = 1.0 / 100.0  # convert dash to velocity
        dl = c * dash + np.random.randn(N) * VAR_L

        dtheta = np.random.randn(N) * VAR_L

        dx = dl * np.cos(np.radians(theta))
        dy = dl * np.sin(np.radians(theta))

        # movement in x,y
        mov = np.vstack((dx, dy))
        # movement with theta=0
        mov = np.vstack((mov, dtheta))

        self.particles = self.particles + mov.T

        self._update_estimated_position()

    def rotate_particles(self, angle):
        """
        Rotate all the particles, it does not have uncertainty.
        :param angle: rotation angle
        """

        self.particles[:, 2] += angle + np.random.randn(N) * VAR_TURN

        self._update_estimated_position()

    def _resample(self, weights):

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
            per = perception[:]
            nx = x[:]

            # gaussian is continuous in reals, but 180 degrees is far away from -179 in the real numbers.
            # the solution is converting the values <90 in a possitive angle.
            if per[2] * nx[2] < 0:
                if per[2] < -90 and (nx[2] > 90):
                    per[2] += 360
                if per[2] > 90 and (nx[2] < 90):
                    nx[2] += 360

            # particle in the  map

            if -55 < x[0] < 55 and -35 < x[1] < 35:  # TODO put map limits as constants
                w1 = multivariate_normal(nx, per, sigma)
            else:
                w1 = 0

            w.append(w1)


        # normalize the weights.
        # w = np.array(w) / sum(w)
        # w is zero, when the measure is very far, then, particles repeat.
        w = np.array(w) / sum(w) if sum(w) > 0 else np.ones(N) / N

        # Resample
        ids = self._resample(w)
        self.particles = self.particles[ids]

        self._update_estimated_position()


    def _update_estimated_position(self):
        self.e_position = np.mean(self.particles, axis=0)
        self.abs_coords = self.e_position[:2]
        self.abs_body_dir = self.e_position[2]


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






