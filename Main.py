import threading

import WingLoader
import MomentDiagram
import ShearDiagram
import TorqueDiagram

import matplotlib.pyplot as plt


class DataCalculator:

    wing = None

    shearX = None
    shearY = None
    momentX = None
    momentY = None
    torqueX = None
    torqueY = None

    def __init__(self, wing):
        self.wing = wing

    def run(self):
        threads = []
        threads.append(threading.Thread(target=self.shear))
        threads.append(threading.Thread(target=self.moment))
        threads.append(threading.Thread(target=self.torque))
        for thread in threads:
            thread.start()
        for thread2 in threads:
            thread2.join()

    def shear(self):
        self.shearX, self.shearY = ShearDiagram.calcShearValues(self.wing)

    def moment(self):
        self.momentX, self.momentY = MomentDiagram.calcMomentValues(self.wing)

    def torque(self):
        self.torqueX, self.torqueY = TorqueDiagram.calcTorqueValues(self.wing)

    def plot(self):
        plt.subplot(2, 2, 1)
        plt.title("Shear Diagram")
        plt.plot(self.shearX, self.shearY)

        plt.subplot(2, 2, 2)
        plt.title("Moment Diagram")
        plt.plot(self.momentX, self.momentY)

        plt.subplot(2, 2, 3)
        plt.title("Torque Diagram")
        plt.plot(self.torqueX, self.torqueY)

        plt.show()


aoa = int(input("Enter angle of attack. Choose 0 or 10 [deg]:"))
v = int(input("Enter velocity [m/s]:"))
rho = float(input("Enter density [kg/m^3]:"))
y_eng = 5.13
z_eng = 1.06492
t_eng = 64.5e3
w_eng = 11566


main = DataCalculator(WingLoader.loadWing(aoa, v, rho, y_eng, z_eng, t_eng, w_eng))
main.run()
main.plot()
