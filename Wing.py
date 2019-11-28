import numpy as np
import scipy as sp

surface_area = 29.29
wing_max = 14.645
stdrange = np.arange(0, wing_max, 0.05)


class Wing:

    material = None

    aoa = 0  # [rad]
    v = 0  # [m/s]
    rho = 0  # [kg/m^3]
    rho_fuel = 0.804e3  # [kg/m^3]

    eng_y = 5.13  # [m]
    eng_z = 1.06492  # [m]
    eng_thrust = 64.5e3  # [m]
    eng_weight = 11566  # [N]

    t = 0.004  # [m] Wall thickness
    n = 12  # [-] Number of stringers
    As = 0.0003  # [m^2] Area of single stringer

    chord = None  # function

    cl0 = None
    cl10 = None

    cd0 = None
    cd10 = None

    cm0 = None
    cm10 = None

    interp_cons = 0

    def __init__(self, material, aoa, v, rho):
        self.material = material
        self.aoa = aoa
        self.v = v
        self.rho = rho

    def cl(self, y):
        return self.cl0(y) + self.interp_cons * (self.cl10(y) - self.cl0(y))

    def cd(self, y):
        return self.cd0(y) + self.interp_cons * (self.cd10(y) - self.cd0(y))

    def cm(self, y):
        return self.cm0(y) + self.interp_cons * (self.cm10(y) - self.cm0(y))

    def normal(self, y):
        return sp.cos(self.aoa) * self.lift(y) + sp.sin(self.aoa) * self.drag(y)

    def lift(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.cl(y) * self.chord(y)

    def drag(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.cd(y) * self.chord(y)

    def moment(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.cm(y) * self.chord(y) ** 2

    def Am(self, y):
        return (2.1 - 0.1 * y) * (0.6 - 0.029 * y)

    def S(self, y):
        return 2 * (2.1 - 0.1 * y) + 2 * (0.6 - 0.029 * y)

    def moi_x(self, y):
        return self.thickness(y) / 6 * (0.6 - 0.029 * y) ** 3 + \
               self.thickness(y) * (2.1 - 0.1 * y) * (0.3 - 0.014 * y) ** 2 + \
               self.As * (0.3 - 0.014 * y) ** 2 * self.nstringers(y)

    def moi_polar(self, y):
        return 4 * self.Am(y) ** 2 * self.thickness(y) / self.S(y)

    def nstringers(self, y):
        if y <= wing_max / 3:
            return 18
        elif y <= wing_max * 2 / 3:
            return 12
        else:
            return 4

    def thickness(self, y):
        if y <= wing_max / 3:
            return 0.016
        elif y <= wing_max * 2 / 3:
            return 0.012
        else:
            return 0.004


class Material:

    E = 0
    G = 0
    rho = 0

    def __init__(self, E, G, rho):
        self.E = E
        self.G = G
        self.rho = rho
