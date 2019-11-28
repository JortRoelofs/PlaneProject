import multiprocessing
import numpy as np
import scipy as sp
from scipy import interpolate

import DeflectionResult
import InertiaDiagram
import LoadDiagram
import Wing
import WingLoader

import matplotlib.pyplot as plt


class DataCalculator:

    poolsize = multiprocessing.cpu_count()

    wing = None

    lift = None
    shear = None
    moment = None
    torsion = None

    moi_x = None
    moi_polar = None

    twist = None
    rotation = None
    deflection = None

    def __init__(self, wing):
        self.wing = wing

    def run(self):
        print("Calculating lift forces")
        self.lift = LoadDiagram.LiftCalculator(self.wing).calc(self.poolsize)
        print("Finished calculating lift forces")
        print("Calculating shear forces")
        self.shear = LoadDiagram.ShearCalculator(self.wing).calc(self.poolsize)
        print("Finished calculating shear forces")
        shearfunc = interpolate.interp1d(Wing.stdrange, self.shear, kind='cubic', fill_value="extrapolate")
        print("Calculating bending moments")
        self.moment = LoadDiagram.MomentCalculator(shearfunc).calc(self.poolsize)
        print("Finished calculating bending moments")
        print("Calculating torsion")
        self.torsion = LoadDiagram.TorsionCalculator(self.wing).calc(self.poolsize)
        print("Finished calculating torsion")
        print("Calculating x moment of inertia")
        self.moi_x = InertiaDiagram.InertiaXCalculator(self.wing).calc(self.poolsize)
        print("Finished calculating x moment of inertia")
        print("Calculating polar moment of inertia")
        self.moi_polar = InertiaDiagram.PolarInertiaCalculator(self.wing).calc(self.poolsize)
        print("Finished calculating polar moment of inertia")
        torsionFunc = interpolate.interp1d(Wing.stdrange, self.torsion, kind='cubic', fill_value="extrapolate")
        print("Calculating twist")
        self.twist = DeflectionResult.TwistCalculator(self.wing, torsionFunc).calc(self.poolsize)
        print("Finished calculating twist")
        momentFunc = interpolate.interp1d(Wing.stdrange, self.moment, kind='cubic', fill_value="extrapolate")
        print("Calculating rotation")
        self.rotation = DeflectionResult.RotationCalculator(self.wing, momentFunc).calc(self.poolsize)
        print("Finished calculating rotation")
        rotationFunc = interpolate.interp1d(Wing.stdrange, self.rotation, kind='cubic', fill_value="extrapolate")
        print("Calculating deflection")
        self.deflection = DeflectionResult.DeflectionCalculator(rotationFunc).calc(self.poolsize)
        print("Finished calculating deflection")
        print("Maximum twist: {0:.2f} [deg]".format(self.twist[-1] * 180 / sp.pi))
        print("Maximum deflection: {0:.2f} [%]".format(self.deflection[-1] / (Wing.wing_max * 2) * 100))

    def plot(self):
        plotDiagram(Wing.stdrange, self.lift, "Lift Distribution", "Wing span [m]", "Lift [N]")
        plotDiagram(Wing.stdrange, self.shear, "Shear Force", "Wing span [m]", "Shear force [N]")
        plotDiagram(Wing.stdrange, self.moment, "Bending Moment", "Wing span [m]", "Bending moment [Nm]")
        plotDiagram(Wing.stdrange, self.torsion, "Torsion", "Wing span [m]", "Torsion [Nm]")
        plotDiagram(Wing.stdrange, self.moi_x, "Moment of Inertia around X-axis", "Wing span[m]", "I$_{xx}$ [m$^4$]")
        plotDiagram(Wing.stdrange, self.moi_polar, "Polar Moment of Inertia", "Wing span [m]", "J [m$^4$]")
        plotDiagram(Wing.stdrange, np.degrees(self.twist), "Wing Twist", "Wing span [m]", "Angle of twist [$^\\deg$]")
        plotDiagram(Wing.stdrange, self.deflection, "Wing Deflection", "Wing span [m]", "Deflection [m]")
        plt.show()


def plotDiagram(x, y, title, xlabel, ylabel):
    plt.figure()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(b=True, which='major', color='#f0f0f0', linestyle='-')
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    plt.axis([min(x), max(x), min(y), max(y)])
    plt.plot(x, y)


if __name__ == '__main__':
    E_mat = float(input("Enter Young's modulus of selected material [Pa]:"))
    G_mat = float(input("Enter shear modulus of selected material [Pa]:"))
    rho_mat = float(input("Enter material density [kg/m^3]:"))
    mat = Wing.Material(E_mat, G_mat, rho_mat)

    n = float(input("Enter load factor [-]:"))
    v = float(input("Enter velocity [m/s]:"))
    rho = float(input("Enter density [kg/m^3]:"))
    weight = float(input("Enter aircraft weight [N]:"))

    main = DataCalculator(WingLoader.loadWing(mat, n, v, rho, weight))
    main.run()
    main.plot()
