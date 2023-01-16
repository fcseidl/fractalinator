
import numpy as np
from scipy.optimize import minimize


def eval(coeffs, x):
    result = 0
    for k in range(coeffs.shape[0]):
        result += coeffs[k] * x ** k
    return result


class GuidedContours:
    """
    Represents a nonzero polynomial of a fixed degree, fitted to take near-zero values
    at a set of points X.
    """

    def __init__(self, degree):
        self._deg = degree
        self._coeffs = np.random.randn(degree + 1, 2) @ np.array([1, 1j])

    def __call__(self, X):
        return eval(self._coeffs, X)

    def fit(self, X, norm=np.linalg.norm):
        """
        Fit polynomial to minimize f(x)^2 averaged over x in X, subject to ||f||=1.
        If the norm for the constraint is not provided, the 2-norm of the coefficient
        vector is used.
        """
        constraint = {
            'type': 'ineq',
            'fun': lambda c: norm(c) - 1
        }
        fun = lambda c: (np.abs(eval(c, X)) ** 2).sum()
        res = minimize(fun, self._coeffs, method='COBYLA', constraints=constraint)
        self._coeffs = res.x
        return self
