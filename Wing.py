class Wing:

    v = 0  # value

    X = 0  # function
    Y = 0  # function
    Z = 0  # function, is actualy 0
    Cp = 0  # function
    Cl = 0  # function
    Cd = 0  # function
    CmGeom = 0  # function
    CmQuarter = 0  # function

    def __init__(self, v, x, y, z, cp, cl, cd, cmgeom, cmquarter):
        self.v = v
        self.X = x
        self.Y = y
        self.Z = z
        self.Cp = cp
        self.Cl = cl
        self.Cd = cd
        self.CmGeom = cmgeom
        self.CmQuarter = cmquarter

    def lift(self, y):
        return 0.5 * 1.225 * self.v ** 2 * self.Cl(y) * self.X(y)

    def drag(self, y):
        return 0.5 * 1.225 * self.v ** 2 * self.Cd(y) * self.X(y)
