import numpy as np
from scipy import interpolate
import Wing


def loadWing(a, v):
    file = "MainWing_a={0:.2f}_v={1:.2f}ms.txt".format(a, v)

    y, c, ai, cl, cd, cmgeom, cmquarter, xcp = np.loadtxt("wings/" + file, skiprows=21, max_rows=38, unpack=True, usecols= (0, 1, 2, 3, 5, 6, 7, 10))

    funcx = interpolate.interp1d(y, c, kind='linear', fill_value="extrapolate")
    funcy = interpolate.interp1d(y, y, kind='linear', fill_value="extrapolate")
    funcz = 0
    funcCp = interpolate.interp1d(y, xcp, kind='cubic', fill_value="extrapolate")
    funcCl = interpolate.interp1d(y, cl, kind='cubic', fill_value="extrapolate")
    funcCd = interpolate.interp1d(y, cd, kind='cubic', fill_value="extrapolate")
    funcCmGeom = interpolate.interp1d(y, cmgeom, kind='cubic', fill_value="extrapolate")
    funcCmQuarter = interpolate.interp1d(y, cmquarter, kind='cubic', fill_value="extrapolate")
    return Wing.Wing(v, funcx, funcy, funcz, funcCp, funcCl, funcCd, funcCmGeom, funcCmQuarter)

