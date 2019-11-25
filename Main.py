import multiprocessing
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
        columns = 4
        rows = 2
        plt.subplot(rows, columns, 1)
        plt.title("Lift Diagram")
        plt.plot(Wing.stdrange, self.lift)

        plt.subplot(rows, columns, 2)
        plt.title("Shear Diagram")
        plt.plot(Wing.stdrange, self.shear)

        plt.subplot(rows, columns, 3)
        plt.title("Moment Diagram")
        plt.plot(Wing.stdrange, self.moment)

        plt.subplot(rows, columns, 4)
        plt.title("Torsion Diagram")
        plt.plot(Wing.stdrange, self.torsion)

        plt.subplot(rows, columns, 5)
        plt.title("X Moment of Inertia Diagram")
        plt.plot(Wing.stdrange, self.moi_x)

        plt.subplot(rows, columns, 6)
        plt.title("Polar Moment of Inertia Diagram")
        plt.plot(Wing.stdrange, self.moi_polar)

        plt.subplot(rows, columns, 7)
        plt.plot(Wing.stdrange, self.twist)

        plt.subplot(rows, columns, 8)
        plt.plot(Wing.stdrange, self.deflection)

        plt.show()


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
