import numpy as np

stdrange = np.arange(0, 14.62, 0.05)


class Wing:

    v = 0  # [m/s]
    rho = 0  # [kg/m^3]

    eng_pos = 0  # [m]
    eng_weight = 0  # [N]

    X = None  # function
    Y = None  # function
    Z = None  # function
    Cp = None  # function
    Cl = None  # function
    Cd = None  # function
    CmGeom = None  # function
    CmQuarter = None  # function

    def __init__(self, v, rho, engine_pos, engine_weight):
        self.v = v
        self.rho = rho
        self.eng_pos = engine_pos
        self.eng_weight = engine_weight

    def lift(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.Cl(y) * self.X(y)

    def drag(self, y):
        return 0.5 * self.rho * self.v ** 2 * self.Cd(y) * self.X(y)
