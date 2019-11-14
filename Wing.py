
class Wing:

    v = 0

    X = 0
    Y = 0
    Z = 0
    Cp = 0
    Cl = 0
    Cd = 0
    CmGeom = 0
    CmQuarter = 0

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
        return 0.5 * 1.225 * self.v ** 2 * self.Cl(y) * self.X(y)
