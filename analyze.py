import sys
from functools import partial
from multiprocessing import Pool
import numpy as np
import scipy as sp
from scipy import integrate, interpolate

import structure
import util


class MoIXXCalculator:

    def __init__(self, load_case):
        self.load_case = load_case

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        func = interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")
        self.load_case.wing.wing_box.moi_xx = func
        return func

    def value(self, y):
        return self.load_case.wing.wing_box.calc_moi_xx(y)


class MoIPolarCalculator:

    def __init__(self, load_case):
        self.load_case = load_case

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        func = interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")
        self.load_case.wing.wing_box.moi_polar = func
        return func

    def value(self, y):
        return self.load_case.wing.wing_box.calc_moi_polar(y)


class ShearCalculator:

    def __init__(self, load_case):
        self.load_case = load_case

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")

    def value(self, y):
        return self.shear(y) + self.fuel(y) + self.weight(y) + self.engine(y)

    def shear(self, y):
        func = lambda y2: self.load_case.wing.lift(y2, self.load_case.density, self.load_case.velocity)
        return integrate.quad(func, y, self.load_case.wing.wing_box.end_y)[0]

    def fuel(self, y):
        return - integrate.quad(self.load_case.wing.fuel_tank.fuel_cross_section, y,
                                self.load_case.wing.wing_box.end_y, limit=100, epsrel=1.49e-06)[0] * structure.FuelTank.rho_fuel * 9.81

    def weight(self, y):
        wing_box = self.load_case.wing.wing_box
        val = integrate.quad(wing_box.calc_material_area, y, wing_box.end_y, epsabs=1.49e-06)[0]
        int2 = integrate.quad(self.load_case.wing.chord, y, wing_box.end_y)[0]
        val2 = 2.06 * 0.001 * int2
        return - 9.81 * wing_box.material.density * (val + val2)

    def engine(self, y):
        if y <= self.load_case.wing.engine.y:
            return - self.load_case.wing.engine.weight
        else:
            return 0

    def print_result(self, results):
        abs_min = abs(min(results))
        abs_max = abs(max(results))
        max_value = abs_max if abs_max > abs_min else abs_min
        print("Magnitude of maximum shear force: {0:.3e} [N]".format(max_value))


class MomentCalculator:

    def __init__(self, load_case, shear):
        self.load_case = load_case
        self.shear = shear

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")

    def value(self, y):
        return integrate.quad(self.shear, y, self.load_case.wing.wing_box.end_y, epsrel=1.49e-06)[0]

    def print_result(self, results):
        abs_min = abs(min(results))
        abs_max = abs(max(results))
        max_value = abs_max if abs_max > abs_min else abs_min
        print("Magnitude of maximum bending moment: {0:.3e} [Nm]".format(max_value))


class RotationCalculator:

    def __init__(self, load_case, moment):
        self.load_case = load_case
        self.moment = moment

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        return interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")

    def value(self, y):
        return self.rotation(y)

    def rotation(self, y):
        func = lambda y2: self.moment(y2) / self.load_case.wing.wing_box.calc_moi_xx(y2)
        return integrate.quad(func, 0, y, limit=200, epsrel=1.49e-06)[0] / self.load_case.wing.wing_box.material.e_modulus


class DeflectionCalculator:

    def __init__(self, load_case, rotation):
        self.load_case = load_case
        self.rotation = rotation

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")

    def value(self, y):
        return self.deflection(y)

    def deflection(self, y):
        return integrate.quad(self.rotation, 0, y, epsabs=1.49e-06)[0]

    def print_result(self, results):
        deflection = results[-1] / (self.load_case.wing.wing_box.end_y * 2) * 100
        print("Maximum deflection: {0:.2f} [%]".format(deflection))
        if deflection > self.load_case.limit_deflection:
            util.print_err("Wing box failed: deflection exceeded limits")


class TorsionCalculator:

    def __init__(self, load_case):
        self.load_case = load_case

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")

    def value(self, y):
        return self.lift_moment(y) + self.engine(y)

    def lift_moment(self, y):
        func = lambda y2: self.load_case.wing.moment(y2, self.load_case.density, self.load_case.velocity)
        return integrate.quad(func, y, self.load_case.wing.wing_box.end_y)[0]

    def engine(self, y):
        if y <= self.load_case.wing.engine.y:
            return self.load_case.wing.engine.thrust * self.load_case.wing.engine.z + self.load_case.wing.engine.weight * self.load_case.wing.engine.x
        else:
            return 0

    def print_result(self, results):
        abs_min = abs(min(results))
        abs_max = abs(max(results))
        max_value = abs_max if abs_max > abs_min else abs_min
        print("Magnitude of maximum torsion: {0:.3e} [Nm]".format(max_value))


class TwistCalculator:

    def __init__(self, load_case, torsion):
        self.load_case = load_case
        self.torsion = torsion

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind='cubic', fill_value="extrapolate")

    def value(self, y):
        return self.twist(y)

    def twist(self, y):
        return integrate.quad(lambda y2: self.torsion(y2) / self.load_case.wing.wing_box.calc_moi_polar(y2),
                              0, y, limit=200)[0] / self.load_case.wing.wing_box.material.shear_modulus

    def print_result(self, results):
        twist = results[-1] * 180 / sp.pi
        print("Maximum twist: {0:.2f} [deg]".format(twist))
        if twist > self.load_case.limit_twist:
            util.print_err("Wing box failed: twist exceeded limits")


class TopPanelStressCalculator:

    def __init__(self, load_case, moment):
        self.load_case = load_case
        self.wing_box = load_case.wing.wing_box
        self.moment = moment

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind="cubic", fill_value="extrapolate")

    def value(self, y):
        return - self.moment(y) * (self.wing_box.calc_height(y) / 2 - self.wing_box.calc_centroid_z(y)) / \
                                 self.wing_box.calc_moi_xx(y)

    def print_result(self, results):
        abs_min = abs(min(results))
        abs_max = abs(max(results))
        max_value = max(results) if abs_max > abs_min else min(results)
        pos = results.index(max_value) * self.load_case.step
        print("Maximum stress in top panel: {0:.3e} [Pa] at {1:.2f} [m]".format(max_value, pos))
        if max_value > self.wing_box.material.yield_stress:
            util.print_err("Wing box failed: top panel stress exceeded yield stress.")


class BottomPanelStressCalculator:

    def __init__(self, load_case, moment):
        self.load_case = load_case
        self.wing_box = load_case.wing.wing_box
        self.moment = moment

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        self.print_result(results)
        return interpolate.interp1d(self.load_case.range, results, kind="cubic", fill_value="extrapolate")

    def value(self, y):
        return self.moment(y) * (self.wing_box.calc_height(y) / 2 + self.wing_box.calc_centroid_z(y)) / \
                                 self.wing_box.calc_moi_xx(y)

    def print_result(self, results):
        abs_min = abs(min(results))
        abs_max = abs(max(results))
        max_value = max(results) if abs_max > abs_min else min(results)
        pos = results.index(max_value) * self.load_case.step
        print("Maximum stress in bottom panel: {0:.3e} [Pa] at {1:.2f} [m]".format(max_value, pos))
        if max_value > self.wing_box.material.yield_stress:
            util.print_err("Wing box failed: bottom panel stress exceeded yield stress.")


class WebBucklingCalculator:

    ks_clamped = util.load_k("stress_coefficients/ks_clamped.txt")
    ks_hinged = util.load_k("stress_coefficients/ks_hinged.txt")

    def __init__(self, load_case, shear, torsion):
        self.load_case = load_case
        self.wing_box = load_case.wing.wing_box
        self.shear = shear
        self.torsion = torsion
        self.shear_factor = self.calc_shear_factor()

    def calc(self, size):
        pool = Pool(size)
        results = pool.map(self.value, self.load_case.range)
        pool.close()
        pool.join()
        min_margin = {}
        for section in self.wing_box.sections:
            min_margin[section] = [sys.float_info.max, False]
        for result in results:
            if result is not None:
                if abs(result[1]) < min_margin[result[0]][0]:
                    min_margin[result[0]][0] = abs(result[1])
                    min_margin[result[0]][1] = result[2]
        self.print_result(min_margin)

    def value(self, y):
        section = self.wing_box.get_active_section(y)
        shear_stress_avg = self.shear(y) / (self.wing_box.calc_height(y) * (section.front_spar_t + section.back_spar_t))
        shear_stress_max = shear_stress_avg * self.shear_factor
        length = section.end_y - section.start_y
        width = self.wing_box.calc_height(y)
        q = self.torsion(y) / (2 * self.wing_box.calc_area_cross_sectional(y))
        crit_stress = [self.critical_stress(section.front_spar_t, length, width) - q / section.front_spar_t, self.critical_stress(section.back_spar_t, length, width) + q / section.back_spar_t]
        return [section, min(crit_stress) / shear_stress_max, crit_stress[0] < crit_stress[1]] # true when lowest safety margin on front spar

    def max_centroid(self, y):
        wing_box_section = self.wing_box.get_active_section(y)
        height = self.wing_box.calc_height(y) / 2 - self.wing_box.calc_centroid_z(y)
        a = self.wing_box.calc_width(y) * wing_box_section.top_panel_t
        az = a * height

        area = height * (wing_box_section.front_spar_t + wing_box_section.back_spar_t)
        a += area
        az += area * height / 2

        for stringer_set in wing_box_section.stringer_sets:
            if stringer_set.surface_top:
                z = height - wing_box_section.top_panel_t - stringer_set.calc_centroid_z()
                area = stringer_set.calc_area()
                a += area
                az += area * z
        return az / a

    def calc_shear_factor(self):
        v_max = 0
        y = 0
        for step in self.load_case.range:
            v = abs(self.shear(step))
            if v > v_max:
                v_max = v
                y = step
        section = self.wing_box.get_active_section(y)
        shear_stress_avg = v_max / (self.wing_box.calc_height(y) * (section.front_spar_t + section.back_spar_t))
        shear_stress_max = v_max * self.max_centroid(y) / (self.wing_box.calc_moi_xx(y) * (section.front_spar_t + section.back_spar_t))
        return shear_stress_max / shear_stress_avg

    def critical_stress(self, thickness, length, width):
        k = self.ks_clamped(length / width)
        return sp.pi ** 2 * k * self.wing_box.material.e_modulus / (12 * (1 - self.wing_box.material.poisson_factor ** 2)) * (thickness / width) ** 2

    def print_result(self, min_margin):
        print("")
        print("Results for shear buckling")
        failure = False
        for section in self.wing_box.sections:
            if min_margin[section][0] < 1: failure = True
            print("Wing box section range: {0:.2f}, {1:.2f} [m]; Lowest margin of safety: {2:.2f} on {3}".format(section.start_y, section.end_y, min_margin[section][0], "front spar" if min_margin[section][1] else "back spar"))
        if failure: util.print_err("Wing box failed due to shear buckling")


class SkinBucklingCalculator:

    kc_b = util.load_k("stress_coefficients/kc_B.txt")
    kc_c = util.load_k("stress_coefficients/kc_C.txt")

    def __init__(self, load_case, top_panel_stress, bottom_panel_stress):
        self.load_case = load_case
        self.wing_box = load_case.wing.wing_box
        self.top_panel_stress = top_panel_stress
        self.bottom_panel_stress = bottom_panel_stress

    def calc(self, size):
        pool = Pool(size)
        results = []
        for plate in self.find_plates():
            results.append(pool.map(partial(self.value, plate=plate), self.load_case.range))
        pool.close()
        pool.join()
        min_margin = {}
        for section in self.wing_box.sections:
            min_margin[section] = [sys.float_info.max, None]
        for results_set in results:
            for result in results_set:
                if result is not None:
                    if 0 < result[1] < min_margin[result[0]][0]:
                        min_margin[result[0]][0] = result[1]
                        min_margin[result[0]][1] = result[2]
        self.print_result(min_margin)

    def value(self, y, plate):
        if plate.start_y <= y <= plate.end_y:
            stress_max = self.top_panel_stress(y) if plate.surface_top else self.bottom_panel_stress(y)
            length = plate.end_y - plate.start_y
            width = plate.width * self.wing_box.calc_width(y)
            ratio = length / width
            if ratio > 5: ratio = 5
            k = self.kc_b(ratio) if plate.side else self.kc_c(ratio)
            stress_crit = - self.critical_stress(k, plate.thickness, width)
            return [self.wing_box.get_active_section(y), stress_crit / stress_max, plate]
        else:
            return None

    def find_plates(self):
        plates = []
        for section in self.wing_box.sections:
            stringer_coords_top = []
            stringer_coords_bottom = []
            for stringer_set in section.stringer_sets:
                if stringer_set.surface_top:
                    if stringer_set.amount == 1:
                        stringer_coords_top.append(stringer_set.start_x)
                    else:
                        stringer_coords_top.extend(
                            np.linspace(stringer_set.start_x, stringer_set.end_x, stringer_set.amount))
                else:
                    if stringer_set.amount == 1:
                        stringer_coords_bottom.append(stringer_set.start_x)
                    else:
                        stringer_coords_bottom.extend(
                            np.linspace(stringer_set.start_x, stringer_set.end_x, stringer_set.amount))
            stringer_coords_top.sort()
            stringer_coords_bottom.sort()
            for i in range(len(stringer_coords_top) - 1):
                width = stringer_coords_top[i + 1] - stringer_coords_top[i]
                side = stringer_coords_top[i + 1] == 1 or stringer_coords_top[i] == 0
                plates.append(util.SkinPlate(section.top_panel_t, section.start_y, section.end_y, width, side, True))
            for j in range(len(stringer_coords_bottom) - 1):
                width = stringer_coords_bottom[j + 1] - stringer_coords_bottom[j]
                side = stringer_coords_bottom[j + 1] == 1 or stringer_coords_bottom[j] == 0
                plates.append(util.SkinPlate(section.bottom_panel_t, section.start_y, section.end_y, width, side, False))
        return plates

    def critical_stress(self, k, thickness, width):
        return sp.pi ** 2 * k * self.wing_box.material.e_modulus / (12 * (1 - self.wing_box.material.poisson_factor ** 2)) * (thickness / width) ** 2

    def print_result(self, min_margin):
        print("")
        print("Results for skin buckling")
        failure = False
        for section in self.wing_box.sections:
            if min_margin[section][0] < 1: failure = True
            print("Wing box section range: {0:.2f}, {1:.2f} [m]; Lowest margin of safety: {2:.2f} on plate with width {3:.2f} [m]".format(section.start_y, section.end_y, min_margin[section][0], min_margin[section][1].width))
        if failure: util.print_err("Wing box failed due to skin buckling")


class ColumnBucklingCalculator:

    def __init__(self, load_case, moment):
        self.moment = moment
        self.load_case = load_case
        self.wing_box = load_case.wing.wing_box

    def calc(self, size):
        pool = Pool(size)
        results = []
        for section in self.wing_box.sections:
            for stringer_set in section.stringer_sets:
                results.append(pool.map(partial(self.value, section=section, stringer_set=stringer_set), self.load_case.range))
        pool.close()
        pool.join()
        min_margin = {}
        for section in self.wing_box.sections:
            min_margin[section] = [sys.float_info.max, None]
        for results_set in results:
            for result in results_set:
                if result is not None:
                    if 0 < result[1] < min_margin[result[0]][0]:
                        min_margin[result[0]][0] = result[1]
                        min_margin[result[0]][1] = result[2]
        self.print_result(min_margin)

    def value(self, y, section, stringer_set):
        if section.start_y <= y <= section.end_y:
            height = self.wing_box.calc_height(y)
            centroid_z = self.wing_box.calc_centroid_z(y)
            z = height / 2 - stringer_set.calc_centroid_z()
            if stringer_set.surface_top:
                z -= centroid_z
                z = -z
            else:
                z += centroid_z
            max_stress = self.moment(y) * z / self.wing_box.calc_moi_xx(y)
            crit_stress = - stringer_set.amount * self.critical_load(section.end_y - section.start_y,
                                stringer_set.calc_moi_xx_parallel_axis(height, centroid_z)) / stringer_set.calc_area()
            return [section, crit_stress / max_stress, stringer_set]
        else:
            return None


    def critical_load(self, length, moi):
        k = 1  # = 1 if both ends are pinned, 4 if both ends are clamped, 1/4 if one end is fixes and one end is free;
               # 1/sqrt(K) = 0.7 if one end is pined and one end is free
        return k * sp.pi ** 2 * self.wing_box.material.e_modulus * moi / length ** 2

    def print_result(self, min_margin):
        print("")
        print("Results for column buckling")
        failure = False
        for section in self.wing_box.sections:
            if min_margin[section][0] < 1: failure = True
            print("Wing box section range: {0:.2f}, {1:.2f} [m]; Lowest margin of safety: {2:.2f} on {3} set with size {4}, {5} [m]".format(section.start_y, section.end_y, min_margin[section][0], min_margin[section][1].stringer_type.name, min_margin[section][1].stringer_width, min_margin[section][1].stringer_height))
        if failure: util.print_err("Wing box failed due to column buckling")
