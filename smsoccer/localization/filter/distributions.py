import math
import numpy as np
from numpy.linalg import inv


def multivariate_normal(x, u, sigma):
    k = len(x)

    a1 = 1.0 / (((2 * math.pi) ** (2 * k)) * math.sqrt(np.linalg.det(sigma)))
    d1 = np.dot((x - u).T, inv(sigma))
    d2 = np.dot(d1, (x - u))
    a2 = - 0.5 * d2

    return a1 * math.exp(a2)


# For test
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # u = np.array([0.0, 0.0])
    # sigma = np.array([[0.1, 0.0], [0.0, 0.1]])
    # x = np.array([0, 0])
    u = np.array([0.0, 0.0, 0])
    sigma = np.array([[0.1, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.0, 0.1]])
    x = np.array([0, 0, 0])
    print multivariate_normal(x, u, sigma)

    y = []

    for i in np.arange(-5, 5, 0.01):
        x = np.array([i, 0, 0])
        y.append(multivariate_normal(x, u, sigma))

    plt.plot(y)
    plt.show()