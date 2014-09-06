from numpy.random import random
import numpy as np
import math

from smsoccer.localization.filter.distributions import multivariate_normal

# Number of particles
from smsoccer.util.geometric import euclidean_distance

N = 500

# Motion variance, Linear and angular
VAR_L = 0.5
VAR_T = 5
# Variance in rotation
VAR_TURN = 10.0

# Update variance: x, y, theta.
# sigma = np.array([[15.0, 0.0, 0.0], [0.0, 15.0, 0.0], [0.0, 0.0, 10.0]])
sigma = np.array([[20.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 140.0]])

SHOW_PARTICLES = True

# Distance visual sensor
VAR_DISTANCE = 16


class ParticleFilter(object):
    def __init__(self):
        self.started = False

        x = -55 + np.random.randn(N) * 110
        # y = -35 + np.random.randn(N) * 70
        y = np.array([-40] * N)
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


    def update_based_on_flags(self, flags):
        """
        Update particles based on flags
        :param flags: seen flags by the robot.
        """
        # Fist flag, nearest.
        f = flags[0]
        real_f = f.real_position()

        # Weights.
        w = [0] * N

        for idx, p in enumerate(self.particles):
            dist_to_real = euclidean_distance(p[:2], real_f)
            z = f.distance - dist_to_real

            # Normal error
            w[idx] = math.exp(-(z ** 2) / (2 * VAR_DISTANCE)) / (math.sqrt(VAR_DISTANCE * 2 * math.pi))


        # Normalize weights
        w = np.array(w) / sum(w) if sum(w) > 0 else np.ones(N) / N
        # Resample
        ids = self._resample(w)
        self.particles = self.particles[ids]

        self._update_estimated_position()


    # def update_particles(self, perception):
    #
    # """
    #     DEPRECATED: update_based_flags is the new
    #     Update the particles based on a perception of the localization.
    #     :param perception: [x,y,theta]
    #     """
    #     # Weights.
    #     w = []
    #     for x in self.particles:
    #         per = perception[:]
    #         nx = x[:]
    #
    #         # gaussian is continuous in reals, but 180 degrees is far away from -179 in the real numbers.
    #         # the solution is converting the values <90 in a possitive angle.
    #         if per[2] * nx[2] < 0:
    #             if per[2] < -90 and (nx[2] > 90):
    #                 per[2] += 360
    #             if per[2] > 90 and (nx[2] < 90):
    #                 nx[2] += 360
    #
    #         # particle in the  map
    #
    #         if -55 < x[0] < 55 and -35 < x[1] < 35:  # TODO put map limits as constants
    #             w1 = multivariate_normal(nx, per, sigma)
    #         else:
    #             w1 = 0
    #
    #         w.append(w1)
    #
    #
    #     # normalize the weights.
    #     # w = np.array(w) / sum(w)
    #     # w is zero, when the measure is very far, then, particles repeat.
    #     w = np.array(w) / sum(w) if sum(w) > 0 else np.ones(N) / N
    #
    #     # Resample
    #     ids = self._resample(w)
    #     self.particles = self.particles[ids]
    #
    #     self._update_estimated_position()


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






