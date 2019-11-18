import threading

import WingLoader
import ShearDiagram

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
        print("TODO")

    def torque(self):
        print("TODO")

    def plot(self):
        plt.subplot(2, 2, 1)
        plt.plot(self.shearX, self.shearY)

        #plt.subplot(2, 2, 2)
        #plt.plot(self.momentX, self.momentY)

        #plt.subplot(2, 2, 3)
        #plt.plot(self.torqueX, self.torqueY)

        #plt.sub

        plt.show()


aoa = int(input("Enter angle of attack. Choose 0 or 10 [deg]:"))
v = int(input("Enter velocity [m/s]:"))
rho = float(input("Enter density [kg/m^3]:"))
y_eng = float(input("Enter engine position, distance from center of wing [m]:"))
w_eng = float(input("Enter engine weight [N]:"))


main = DataCalculator(WingLoader.loadWing(aoa, v, rho, y_eng, w_eng))
main.run()
main.plot()