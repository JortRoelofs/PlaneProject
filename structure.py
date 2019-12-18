import numpy as np
import scipy as sp


class Wing:

    def __init__(self):
        self.name = ""          # name
        self.wing_box = None    # WingBox object
        self.engine = None      # Engine object
        self.fuel_tank = None   # FuelTank object
        self.chord = None       # c(y) [m]
        self.cl0 = None         # cl(y) [m] at aoa =  0 [deg]
        self.cl10 = None        # cl(y) [m] at aoa = 10 [deg]
        self.cd0 = None         # cd(y) [m] at aoa =  0 [deg]
        self.cd10 = None        # cd(y) [m] at aoa = 10 [deg]
        self.cm0 = None         # cm(y) [m] at aoa =  0 [deg]
        self.cm10 = None        # cm(y) [m] at aoa = 10 [deg]
        self.interp_cons = 0    # constant
        self.aoa = 0            # [rad]
        self.surface_area = 0   # [m^2]

    def cl(self, y):
        return self.cl0(y) + self.interp_cons * (self.cl10(y) - self.cl0(y))

    def cd(self, y):
        return self.cd0(y) + self.interp_cons * (self.cd10(y) - self.cd0(y))

    def cm(self, y):
        return self.cm0(y) + self.interp_cons * (self.cm10(y) - self.cm0(y))

    def normal(self, y, density, velocity):
        return sp.cos(self.aoa) * self.lift(density, velocity, y) + sp.sin(self.aoa) * self.drag(density, velocity, y)

    def lift(self, y, density, velocity):
        return 0.5 * density * velocity ** 2 * self.cl(y) * self.chord(y)

    def drag(self, y, density, velocity):
        return 0.5 * density * velocity ** 2 * self.cd(y) * self.chord(y)

    def moment(self, y, density, velocity):
        return 0.5 * density * velocity ** 2 * self.cm(y) * self.chord(y) ** 2


class WingBox:

    def __init__(self):
        self.name = None
        self.start_y = 0
        self.end_y = 0
        self.width = None
        self.height = None
        self.material = None
        self.sections = []
        self.moi_xx = None
        self.moi_polar = None

    def calc_width(self, y):
        return self.width.evaluate(y=y)

    def calc_height(self, y):
        return self.height.evaluate(y=y)

    def calc_material_area(self, y):
        section = self.get_active_section(y)
        return section.calc_material_area(self.calc_width(y), self.calc_height(y))

    def calc_area_cross_sectional(self, y):
        section = self.get_active_section(y)
        return section.calc_area_cross_sectional(self.calc_width(y), self.calc_height(y))

    def calc_circumference(self, y):
        return 2 * (self.calc_width(y) + self.calc_height(y))

    def calc_centroid_x(self, y):
        return self.get_active_section(y).calc_centroid_x(self.calc_width(y), self.calc_height(y))

    def calc_centroid_z(self, y):
        return self.get_active_section(y).calc_centroid_z(self.calc_width(y), self.calc_height(y))

    def calc_moi_xx(self, y):
        if self.moi_xx is not None:
            return self.moi_xx(y)
        else:
            width = self.calc_width(y)
            height = self.calc_height(y)
            section = self.get_active_section(y)
            centroid_z = self.calc_centroid_z(y)
            moi_xx = section.calc_moi_xx_parallel_axis(width, height, centroid_z)
            inside_height = height - section.top_panel_t - section.bottom_panel_t
            for stringer_set in section.stringer_sets:
                moi_xx += stringer_set.calc_moi_xx_parallel_axis(inside_height, centroid_z)
            return moi_xx

    def calc_moi_zz(self, y):
        width = self.calc_width(y)
        height = self.calc_height(y)
        section = self.get_active_section(y)
        centroid_x = self.calc_centroid_x(y)
        moi_zz = section.calc_moi_zz(width, height) + \
            section.calc_material_area(width, height) * centroid_x ** 2
        inside_width = width - section.front_spar_t - section.bottom_spar_t
        for stringer_set in section.stringer_sets:
            moi_zz += stringer_set.calc_moi_zz_parallel_axis(inside_width, centroid_x)
        return moi_zz

    def calc_moi_polar(self, y):
        if self.moi_polar is not None:
            return self.moi_polar(y)
        else:
            section = self.get_active_section(y)
            integral = self.calc_width(y) * (section.top_panel_t + section.bottom_panel_t) / (section.top_panel_t * section.bottom_panel_t) + \
                self.calc_height(y) * (section.front_spar_t + section.back_spar_t) / (section.front_spar_t * section.back_spar_t)
            return 4 * self.calc_area_cross_sectional(y) ** 2 / integral

    def get_active_section(self, y):
        for section in self.sections:
            if section.start_y <= y <= section.end_y:
                return section
        return None


class WingBoxSection:

    def __init__(self):
        self.start_y = 0.0
        self.end_y = 0.0
        self.front_spar_t = 0
        self.back_spar_t = 0
        self.top_panel_t = 0
        self.bottom_panel_t = 0
        self.stringer_sets = []

    def calc_material_area(self, width, height):
        return width * (self.top_panel_t + self.bottom_panel_t) + height * (self.front_spar_t + self.back_spar_t)

    def calc_area_cross_sectional(self, width, height):
        return (width - self.front_spar_t - self.back_spar_t) * (height - self.top_panel_t - self.bottom_panel_t)

    def calc_centroid_x(self, width, height):
        ax = height * width * (self.back_spar_t - self.front_spar_t) / 2
        a = height * (self.front_spar_t + self.back_spar_t)
        for stringer_set in self.stringer_sets:
            area = stringer_set.calc_area()
            x = (width - self.front_spar_t - self.back_spar_t) * (stringer_set.calc_centroid_x() - 0.5)
            ax += area * x
            a += area
        return ax / a

    def calc_centroid_z(self, width, height):
        az = width * height * (self.top_panel_t - self.bottom_panel_t) / 2
        a = height * (self.top_panel_t + self.bottom_panel_t)
        for stringer_set in self.stringer_sets:
            area = stringer_set.calc_area()
            z = (height - self.top_panel_t - self.bottom_panel_t) * 0.5 - stringer_set.calc_centroid_z()
            if not stringer_set.surface_top:
                z = -z
            az += area * z
            a += area
        return az / a

    def calc_moi_xx(self, width, height):
        moi = (self.front_spar_t + self.back_spar_t) * height ** 3 / 12
        moi += width * self.top_panel_t ** 3 / 12 + width * self.top_panel_t * ((height + self.top_panel_t) / 2) ** 2
        moi += width * self.bottom_panel_t ** 3 / 12 + width * self.bottom_panel_t * ((height + self.bottom_panel_t) / 2) ** 2
        return moi

    def calc_moi_xx_parallel_axis(self, width, height, location):
        moi = self.calc_moi_xx(width, height)
        moi += (self.front_spar_t + self.back_spar_t) * height * location ** 2
        moi += width * self.top_panel_t * ((height + self.top_panel_t) / 2 - location) ** 2
        moi += width * self.bottom_panel_t * ((height + self.bottom_panel_t) / 2 + location) ** 2
        return moi

    def calc_moi_zz(self, width, height):
        return width ** 3 * height / 12 - (width - self.front_spar_t - self.back_spar_t) ** 3 * (height - self.top_panel_t - self.bottom_panel_t) / 12

    def calc_moi_polar(self, y, width, height):
        print(self.start_y + y)

    def __hash__(self):
        return hash((self.start_y, self.end_y, self.front_spar_t, self.back_spar_t, self.top_panel_t, self.bottom_panel_t))

    def __eq__(self, other):
        return (self.start_y, self.end_y, self.front_spar_t, self.back_spar_t, self.top_panel_t, self.bottom_panel_t) == (other.start_y, other.end_y, other.front_spar_t, other.back_spar_t, other.top_panel_t, other.bottom_panel_t)


class FuelTank:

    rho_fuel = 0.804e3  # [kg/m^3]

    def __init__(self):
        self.start_y = 0  # [m]
        self.end_y = 0  # [m]
        self.wing_box = None

    def fuel_cross_section(self, y):
        if self.start_y <= y <= self.end_y:
            return self.wing_box.calc_area_cross_sectional(y)
        else:
            return 0.0


class Engine:

    def __init__(self):
        self.x = 0  # [m]
        self.y = 0  # [m]
        self.z = 0  # [m]
        self.thrust = 0  # [N]
        self.weight = 0  # [N]


class StringerType:

    def __init__(self):
        self.name = ""
        self.area = None
        self.centroid_x = None
        self.centroid_z = None
        self.moi_xx = None
        self.moi_zz = None

    def calc_area(self, width, height, thickness):
        return self.area.evaluate(w=width, h=height, t=thickness)

    def calc_centroid_x(self, width, height, thickness):
        return self.centroid_x.evaluate(w=width, h=height, t=thickness)

    def calc_centroid_z(self, width, height, thickness):
        return self.centroid_z.evaluate(w=width, h=height, t=thickness)

    def calc_moi_xx(self, width, height, thickness):
        return self.moi_xx.evaluate(w=width, h=height, t=thickness, a=self.calc_area(width, height, thickness),
                                    z=self.calc_centroid_z(width, height, thickness))

    def calc_moi_zz(self, width, height, thickness):
        return self.moi_zz.evaluate(w=width, h=height, t=thickness, a=self.calc_area(width, height, thickness),
                                    z=self.calc_centroid_x(width, height, thickness))


class StringerSet:

    def __init__(self):
        self.stringer_type = None
        self.amount = 0
        self.stringer_width = 0
        self.stringer_height = 0
        self.stringer_thickness = 0
        self.start_x = 0  # fraction of wing box width [-]
        self.end_x = 0  # fraction [-]
        self.surface_top = True  # True if top, False if bottom

    def calc_area(self):
        return self.stringer_type.calc_area(self.stringer_width, self.stringer_height, self.stringer_thickness) * \
            self.amount

    def calc_centroid_x(self, width):
        return width * (self.start_x + (self.end_x - self.start_x) / 2)

    def calc_centroid_z(self):
        centroid = self.stringer_type.calc_centroid_z(self.stringer_width, self.stringer_height, self.stringer_thickness)
        if self.stringer_height - centroid < centroid: centroid = self.stringer_height - centroid
        return centroid

    def calc_moi_xx(self):
        return self.stringer_type.calc_moi_xx(self.stringer_width, self.stringer_height, self.stringer_thickness) * \
            self.amount

    def calc_moi_xx_parallel_axis(self, height, location):
        centroid = self.calc_centroid_z()
        if centroid > (self.stringer_height - centroid):
            centroid = (self.stringer_height - centroid)
        z = height / 2 - centroid
        if self.surface_top:
            z -= location
        else:
            z += location
        return self.calc_moi_xx() + self.calc_area() * (centroid - location) ** 2

    def calc_moi_zz(self, width):
        centroid_stringer = self.stringer_type.calc_centroid_x(self.stringer_width, self.stringer_height,
                                                               self.stringer_thickness)
        if centroid_stringer > (self.stringer_width - centroid_stringer):
            centroid_stringer = self.stringer_width - centroid_stringer
        start_x = self.start_x * width + centroid_stringer
        end_x = self.end_x * width - centroid_stringer
        centroid = self.calc_centroid_x(width)
        area = self.stringer_type.calc_area(self.stringer_width, self.stringer_height, self.stringer_thickness)
        moi_zz = self.amount * self.stringer_type.calc_moi_zz(self.stringer_width, self.stringer_height,
                                                              self.stringer_thickness)
        stringer_x = np.linspace(start_x, end_x, self.amount)
        for x in stringer_x:
            moi_zz += area * (centroid - x) ** 2
        return moi_zz

    def calc_moi_zz_parallel_axis(self, width, location):
        centroid_stringer = self.stringer_type.calc_centroid_x(self.stringer_width, self.stringer_height,
                                                               self.stringer_thickness)
        if centroid_stringer > (self.stringer_width - centroid_stringer):
            centroid_stringer = self.stringer_width - centroid_stringer
        start_x = self.start_x * width + centroid_stringer
        end_x = self.end_x * width - centroid_stringer
        area = self.stringer_type.calc_area(self.stringer_width, self.stringer_height, self.stringer_thickness)
        moi_zz = self.amount * self.stringer_type.calc_moi_zz(self.stringer_width, self.stringer_height,
                                                              self.stringer_thickness)
        stringer_x = np.linspace(start_x, end_x, self.amount)
        for x in stringer_x:
            moi_zz += area * (location - x) ** 2
        return moi_zz


class Material:

    def __init__(self):
        self.name = ""
        self.e_modulus = 0
        self.shear_modulus = 0
        self.poisson_factor = 0
        self.yield_stress = 0
        self.density = 0


class LoadCase:

    def __init__(self):
        self.range = None
        self.wing = None
        self.step = 0
        self.load_factor = 0
        self.velocity = 0
        self.density = 0
        self.aircraft_weight = 0
        self.limit_deflection = 0
        self.limit_twist = 0
