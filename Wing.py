
class Wing:

    X = []
    Y = []
    Cl = []
    Cd = []
    Cm = []

    def __init__(self, x, y, cl, cd, cm):
        self.X = x
        self.Y = y
        self.Cl = cl
        self.Cd = cd
        self.Cm = cm

    def getYCoord(self, xcoord):
        return self.Y[self.getXCoordIndex(xcoord)]

    def getCl(self, xcoord):
        return self.Cl[self.getXCoordIndex(xcoord)]

    def getCd(self, xcoord):
        return self.Cd[self.getXCoordIndex(xcoord)]

    def getCm(self, xcoord):
        return self.Cm[self.getXCoordIndex(xcoord)]

    def getXCoordIndex(self, xcoord):
        if xcoord <= self.x[0]:
            return 0
        elif xcoord >= self.x[-1]:
            return len(self.x) - 1
        else:
            for i in range(1, len(self.x)):
                if xcoord <= self.x[i]:
                    if xcoord <= (self.x[i] + self.x[i - 1]) / 2:
                        return i - 1
                    else:
                        return i
