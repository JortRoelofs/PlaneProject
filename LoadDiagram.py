from multiprocessing import Pool
from scipy import integrate

import Wing


class LiftCalculator:

    wing = None

    def __init__(self, wing):
        self.wing = wing

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.wing.lift(y)


class ShearCalculator:

    wing = None

    def __init__(self, wing):
        self.wing = wing

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return - self.shear(y) + self.fuel(y) + self.weight(y)

    def shear(self, y):
        val = integrate.quad(self.wing.lift, y, Wing.wing_max)[0]
        if y <= self.wing.eng_y:
            return val - self.wing.eng_weight
        else:
            return val

    def fuel(self, y):
        return integrate.quad(self.wing.Am, y, Wing.wing_max)[0] * self.wing.rho_fuel

    def weight(self, y):
        val = 9.81 * self.wing.material.rho * self.wing.t * integrate.quad(self.wing.Am, y, Wing.wing_max)[0]
        val2 = 2.06 * 9.81 * self.wing.material.rho * 0.001 * integrate.quad(self.wing.chord, y, Wing.wing_max)[0]
        return val + val2


class MomentCalculator:

    shearfunc = None

    def __init__(self, shearfunc):
        self.shearfunc = shearfunc

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return - integrate.quad(self.shearfunc, y, Wing.wing_max)[0]


class TorsionCalculator:

    wing = None

    def __init__(self, wing):
        self.wing = wing

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, Wing.stdrange)
        pool.close()
        pool.join()
        return results

    def value(self, y):
        return self.torsion(y)

    def torsion(self, y):
        val = integrate.quad(self.wing.moment, y, Wing.wing_max)[0]
        if y <= self.wing.eng_y:
            return val + self.wing.eng_thrust * self.wing.eng_z
        else:
            return val
