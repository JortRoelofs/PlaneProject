import numpy as np
from scipy import interpolate
import Wing


def loadWing(a, v, rho, eng_y, eng_z, eng_thrust, eng_weight):
    file = "MainWing_a={0:.2f}_v={1:.2f}ms.txt".format(a, 10)

    y, c, ai, cl, cd, cmgeom, cmquarter, xcp = np.loadtxt("wings/" + file, skiprows=21, max_rows=38, unpack=True,
                                                          usecols=(0, 1, 2, 3, 5, 6, 7, 10), encoding="cp1252")
    wing = Wing.Wing(v, rho, eng_y, eng_z, eng_thrust, eng_weight)
    wing.X = interpolate.interp1d(y, c, kind='linear', fill_value="extrapolate")
    wing.Y = interpolate.interp1d(y, y, kind='linear', fill_value="extrapolate")
    wing.Z = 0
    wing.Cp = interpolate.interp1d(y, xcp, kind='cubic', fill_value="extrapolate")
    wing.Cl = interpolate.interp1d(y, cl, kind='cubic', fill_value="extrapolate")
    wing.Cd = interpolate.interp1d(y, cd, kind='cubic', fill_value="extrapolate")
    wing.CmGeom = interpolate.interp1d(y, cmgeom, kind='cubic', fill_value="extrapolate")
    wing.CmQuarter = interpolate.interp1d(y, cmquarter, kind='cubic', fill_value="extrapolate")
    return wing
