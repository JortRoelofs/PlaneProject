
class Wing:

    X = []
    Y = []
    Z = []
    Cl = []
    Cd = []
    Cm = []

    def __init__(self, x, y, z, cl, cd, cm):
        self.X = x
        self.Y = y
        self.Z = z
        self.Cl = cl
        self.Cd = cd
        self.Cm = cm

    def getXCoord(self, ycoord):
        return self.X[self.getYCoordIndex(ycoord)]

    def getZCoord(self, ycoord):
        return self.Z[self.getYCoordIndex(ycoord)]

    def getCl(self, ycoord):
        return self.Cl[self.getYCoordIndex(ycoord)]

    def getCd(self, ycoord):
        return self.Cd[self.getYCoordIndex(ycoord)]

    def getCm(self, ycoord):
        return self.Cm[self.getYCoordIndex(ycoord)]

    def getYCoordIndex(self, ycoord):
        if ycoord <= self.Y[0]:
            return 0
        elif ycoord >= self.Y[-1]:
            return len(self.Y) - 1
        else:
            for i in range(1, len(self.Y)):
                if ycoord <= self.Y[i]:
                    if ycoord <= (self.Y[i] + self.Y[i - 1]) / 2:
                        return i - 1
                    else:
                        return i
