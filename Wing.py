import numpy as np

stdrange = np.arange(0, 14.62, 0.05)


class Wing:

    v = 0  # [m/s]
    rho = 0  # [kg/m^3]

    eng_y = 0  # [m]
    eng_z = 0  # [m]
    eng_thrust = 0  # [m]
    eng_weight = 0  # [N]

    X = None  # function
    Y = None  # function
    Z = None  # function
    Cp = None  # function
    Cl = None  # function
    Cd = None  # function
    CmGeom = None  # function
    CmQuarter = None  # function

    def __init__(self, v, rho, eng_y, eng_z, eng_thrust, eng_weight):
        self.v = v
        self.rho = rho
        self.eng_y = eng_y
        self.eng_z = eng_z
        self.eng_thrust = eng_thrust
        self.eng_weight = eng_weight

    def lift(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.Cl(y) * self.X(y)

    def drag(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.Cd(y) * self.X(y)
