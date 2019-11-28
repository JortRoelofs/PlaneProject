from multiprocessing import Pool
from scipy import integrate

import Wing


class RotationCalculator:

    wing = None
    momentFunc = None

    def __init__(self, wing, momentFunc):
        self.wing = wing
        self.momentFunc = momentFunc

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.rotation(y)

    def rotation(self, y):
        return integrate.quad(lambda y2: self.momentFunc(y2) / self.wing.moi_x(y2), 0, y, limit=100)[0] \
               / self.wing.material.E


class DeflectionCalculator:

    rotationFunc = None

    def __init__(self, rotationFunc):
        self.rotationFunc = rotationFunc

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.deflection(y)

    def deflection(self, y):
        return integrate.quad(self.rotationFunc, 0, y, epsabs=1.49e-06)[0]


class TwistCalculator:

    wing = None
    torsionFunc = None

    def __init__(self, wing, torsionFunc):
        self.wing = wing
        self.torsionFunc = torsionFunc

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.twist(y)

    def twist(self, y):
        return 1 / self.wing.material.G * \
               integrate.quad(lambda y2: self.torsionFunc(y2) / self.wing.moi_polar(y2), 0, y, limit=100)[0]
