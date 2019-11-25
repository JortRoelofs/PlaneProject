import numpy as np
import scipy as sp
from scipy import interpolate

import Wing


class XFLRWing:

    CL = 0

    chord = None
    cl = None
    cd = None
    cm = None

    def __init__(self, filename):
        file = open(filename, "r")
        for i in range(21):
            line = file.readline()
            if "CL" in line:
                self.CL = float(line.split("=")[1].strip())
        file.close()

        y, c, cl, cd, cm, = np.loadtxt(filename, skiprows=21, max_rows=38, unpack=True, usecols=(0, 1, 3, 5, 7),
                                       encoding="cp1252")

        self.chord = interpolate.interp1d(y, c, kind='linear', fill_value="extrapolate")
        self.cl = interpolate.interp1d(y, cl, kind='cubic', fill_value="extrapolate")
        self.cd = interpolate.interp1d(y, cd, kind='cubic', fill_value="extrapolate")
        self.cm = interpolate.interp1d(y, cm, kind='cubic', fill_value="extrapolate")


def loadWing(material, n, v, rho, weight):
    file010 = "MainWing_a=0.00_v=10.00ms.txt"
    file1010 = "MainWing_a=10.00_v=10.00ms.txt"

    xflr0 = XFLRWing("wings/" + file010)
    xflr10 = XFLRWing("wings/" + file1010)

    CLreq = (n * weight) / (0.5 * rho * v ** 2 * Wing.surface_area)
    interp_cons = (CLreq - xflr0.CL) / (xflr10.CL - xflr0.CL)
    aoa = sp.arcsin(interp_cons * sp.sin(10 * sp.pi / 180))  # in radians
    print("Angle of attack: %d [deg]" % (aoa * 180 / sp.pi))

    wing = Wing.Wing(material, aoa, v, rho)
    wing.interp_cons = interp_cons
    wing.cl0 = xflr0.cl
    wing.cl10 = xflr10.cl
    wing.cd0 = xflr0.cd
    wing.cd10 = xflr10.cd
    wing.cm0 = xflr0.cm
    wing.cm10 = xflr10.cm
    wing.chord = xflr0.chord

    return wing
