import multiprocessing
import numpy as np

import analyze
import parse

import matplotlib.pyplot as plt


class DataCalculator:

    poolsize = multiprocessing.cpu_count()

    def __init__(self, load_case):
        self.load_case = load_case

        self.shear = None
        self.moment = None
        self.rotation = None
        self.deflection = None

        self.torsion = None
        self.twist = None

        self.moi_analyzed = False
        self.moi_xx = None
        self.moi_polar = None

        self.top_panel_stress = None
        self.bottom_panel_stress = None
        self.web_buckling = None
        self.skin_buckling = None
        self.column_buckling = None

    def analyze_moi(self):
        if not self.moi_analyzed:
            self.moi_xx = analyze.MoIXXCalculator(self.load_case).calc(self.poolsize)
            self.moi_polar = analyze.MoIPolarCalculator(self.load_case).calc(self.poolsize)
            plot_diagram(self.load_case.range, self.moi_xx, "Moment of Inertia around X-axis", "Wing span[m]", "I$_{xx}$ [m$^4$]")
            plot_diagram(self.load_case.range, self.moi_polar, "Polar Moment of Inertia", "Wing span [m]", "J [m$^4$]")
            self.moi_analyzed = True

    def analyze_deflection(self):
        self.analyze_moi()
        self.shear = analyze.ShearCalculator(self.load_case).calc(self.poolsize)
        self.moment = analyze.MomentCalculator(self.load_case, self.shear).calc(self.poolsize)
        self.rotation = analyze.RotationCalculator(self.load_case, self.moment).calc(self.poolsize)
        self.deflection = analyze.DeflectionCalculator(self.load_case, self.rotation).calc(self.poolsize)
        plot_diagram(self.load_case.range, self.shear, "Shear Force", "Wing span [m]", "Shear force [N]")
        plot_diagram(self.load_case.range, self.moment, "Bending Moment", "Wing span [m]", "Bending moment [Nm]")
        plot_diagram(self.load_case.range, self.rotation, "Rotation", "Wing span [m]", "Rotation [rad]")
        plot_diagram(self.load_case.range, self.deflection, "Wing Deflection", "Wing span [m]", "Deflection [m]")

    def analyze_twist(self):
        self.analyze_moi()
        self.torsion = analyze.TorsionCalculator(self.load_case).calc(self.poolsize)
        self.twist = analyze.TwistCalculator(self.load_case, self.torsion).calc(self.poolsize)
        plot_diagram(self.load_case.range, lambda y: np.degrees(self.twist(y)), "Wing Twist", "Wing span [m]", "Angle of twist [$^\\deg$]")

    def analyze_stress(self):
        self.analyze_moi()
        if self.shear is None:
            self.shear = analyze.ShearCalculator(self.load_case).calc(self.poolsize)
        if self.moment is None:
            self.moment = analyze.MomentCalculator(self.load_case, self.shear).calc(self.poolsize)
        if self.torsion is None:
            self.torsion = analyze.TorsionCalculator(self.load_case).calc(self.poolsize)
        self.top_panel_stress = analyze.TopPanelStressCalculator(self.load_case, self.moment).calc(self.poolsize)
        self.bottom_panel_stress = analyze.BottomPanelStressCalculator(self.load_case, self.moment).calc(self.poolsize)
        self.web_buckling = analyze.WebBucklingCalculator(self.load_case, self.shear, self.torsion).calc(self.poolsize)
        self.skin_buckling = analyze.SkinBucklingCalculator(self.load_case, self.top_panel_stress, self.bottom_panel_stress).calc(self.poolsize)
        self.column_buckling = analyze.ColumnBucklingCalculator(self.load_case, self.moment).calc(self.poolsize)


    def show_plots(self):
        plt.show()


def plot_diagram(x, y_function, title, xlabel, ylabel):
    plt.figure()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(b=True, which='major', color='#f0f0f0', linestyle='-')
    plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
    y = []
    for i in x:
        y.append(y_function(i))
    plt.axis([min(x), max(x), min(y), max(y)])
    plt.plot(x, y_function(x))


if __name__ == '__main__':
    input_load_cases_str = input("Enter load case:")
    input_load_case = parse.load_load_case(input_load_cases_str)

    main = DataCalculator(input_load_case)
    main.analyze_deflection()
    main.analyze_twist()
    main.analyze_stress()
    #main.show_plots()
