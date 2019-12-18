import structure
import util


materials = []
stringer_types = []


def load_wing(file):
    f = open("wings/%s.wing" % file, 'r')
    lines = f.readlines()
    f.close()
    return parse_wing(lines)


def parse_wing(lines):
    wing = structure.Wing()
    engine_lines = []
    engine_active = False
    fuel_tank_lines = []
    fuel_tank_active = False
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if engine_active:
            if '}' in line:
                engine_active = False
                engine_lines.append(line.replace('}', ''))
                wing.engine = parse_engine(engine_lines)
            else:
                engine_lines.append(line)
        elif fuel_tank_active:
            if '}' in line:
                fuel_tank_active = False
                fuel_tank_lines.append(line.replace('}', ''))
                wing.fuel_tank = parse_fuel_tank(fuel_tank_lines)
            else:
                fuel_tank_lines.append(line)
        elif tokens[0] == "name":
            wing.name = tokens[1]
        elif tokens[0] == "wing_box":
            wing.wing_box = load_wing_box(tokens[1])
        elif tokens[0] == "surface_area":
            wing.surface_area = float(tokens[1])
        elif tokens[0] == "engine":
            engine_lines.clear()
            engine_lines.append(tokens[1].replace('{', ''))
            engine_active = True
        elif tokens[0] == "fuel_tank":
            fuel_tank_lines.clear()
            fuel_tank_lines.append(tokens[1].replace('{', ''))
            fuel_tank_active = True
    wing.fuel_tank.wing_box = wing.wing_box
    return wing


def parse_engine(lines):
    engine = structure.Engine()
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if tokens[0] == "position":
            pos = tokens[1].split(',')
            engine.x = float(pos[0])
            engine.y = float(pos[1])
            engine.z = float(pos[2])
        elif tokens[0] == "thrust":
            engine.thrust = float(tokens[1])
        elif tokens[0] == "weight":
            engine.weight = float(tokens[1])
    return engine


def parse_fuel_tank(lines):
    fuel_tank = structure.FuelTank()
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if tokens[0] == "range":
            fuel_tank_range = tokens[1].split(',')
            fuel_tank.start_y = float(fuel_tank_range[0])
            fuel_tank.end_y = float(fuel_tank_range[1])
    return fuel_tank


def load_wing_box(file):
    f = open("wingboxes/%s.wbo" % file, 'r')
    lines = f.readlines()
    f.close()
    return parse_wing_box(lines)


def parse_wing_box(lines):
    wing_box = structure.WingBox()
    section_lines = []
    level = 0
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if level > 0:
            if '{' in line:
                level += 1
                section_lines.append(line)
            elif '}' in line:
                level -= 1
                section_lines.append(line)
                if level == 0:
                    section_lines[-1] = section_lines[-1].replace('}', '')
                    wing_box.sections.append(parse_wing_box_section(section_lines))
            else:
                section_lines.append(line)
        elif tokens[0] == "name":
            wing_box.name = tokens[1]
        elif tokens[0] == "range":
            wing_box_range = tokens[1].split(',')
            wing_box.start_y = float(wing_box_range[0])
            wing_box.end_y = float(wing_box_range[1])
        elif tokens[0] == "width":
            wing_box.width = util.GeometryFunction(tokens[1])
        elif tokens[0] == "height":
            wing_box.height = util.GeometryFunction(tokens[1])
        elif tokens[0] == "material":
            wing_box.material = get_material(tokens[1])
        elif tokens[0] == "section":
            section_lines.clear()
            section_lines.append(tokens[1].replace('{', ''))
            level += 1
    return wing_box


def parse_wing_box_section(lines):
    wing_box_section = structure.WingBoxSection()
    stringer_set_lines = []
    level = 0
    corner_set_active = False
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if level > 0:
            if '{' in line:
                level += 1
            elif '}' in line:
                level -= 1
                stringer_set_lines.append(line)
                if level == 0:
                    stringer_set_lines[-1].replace('}', '')
                    if corner_set_active:
                        corner_set_active = False
                        stringer_set_lines.extend(["name:L-stringer", "amount:2", "range:0.0,1.0", "surface:bottom"])
                        wing_box_section.stringer_sets.append(parse_stringer_set(stringer_set_lines))
                        stringer_set_lines[-1] = stringer_set_lines[-1].replace("bottom", "top")
                        wing_box_section.stringer_sets.append(parse_stringer_set(stringer_set_lines))
                    else:
                        wing_box_section.stringer_sets.append(parse_stringer_set(stringer_set_lines))
            else:
                stringer_set_lines.append(line)
        elif tokens[0] == "range":
            section_range = tokens[1].split(',')
            wing_box_section.start_y = float(section_range[0])
            wing_box_section.end_y = float(section_range[1])
        elif tokens[0] == "spar_thickness":
            spar_thickness = tokens[1].split(',')
            wing_box_section.front_spar_t = float(spar_thickness[0])
            wing_box_section.back_spar_t = float(spar_thickness[1])
        elif tokens[0] == "panel_thickness":
            panel_thickness = tokens[1].split(',')
            wing_box_section.top_panel_t = float(panel_thickness[0])
            wing_box_section.bottom_panel_t = float(panel_thickness[1])
        elif tokens[0] == "corner":
            stringer_set_lines.clear()
            stringer_set_lines.append(tokens[1].replace('{', ''))
            corner_set_active = True
            level += 1
        elif tokens[0] == "stringer_set":
            stringer_set_lines.clear()
            stringer_set_lines.append(tokens[1].replace('{', ''))
            level += 1
    return wing_box_section


def parse_stringer_set(lines):
    stringer_set = structure.StringerSet()
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if tokens[0] == "name":
            stringer_set.stringer_type = get_stringer_type(tokens[1])
        elif tokens[0] == "amount":
            stringer_set.amount = int(tokens[1])
        elif tokens[0] == "stringer_width":
            stringer_set.stringer_width = float(tokens[1])
        elif tokens[0] == "stringer_height":
            stringer_set.stringer_height = float(tokens[1])
        elif tokens[0] == "stringer_thickness":
            stringer_set.stringer_thickness = float(tokens[1])
        elif tokens[0] == "range":
            stringers_range = tokens[1].split(',')
            stringer_set.start_x = float(stringers_range[0])
            stringer_set.end_x = float(stringers_range[1])
        elif tokens[0] == "surface":
            stringer_set.surface_top = tokens[1] == "top"
    return stringer_set


def load_material(file):
    f = open("materials/%s.mat" % file, 'r')
    lines = f.readlines()
    f.close()
    return parse_material(lines)


def parse_material(lines):
    material = structure.Material()
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if tokens[0] == "name":
            material.name = tokens[1]
        elif tokens[0] == "e-modulus":
            material.e_modulus = float(tokens[1])
        elif tokens[0] == "shear_modulus":
            material.shear_modulus = float(tokens[1])
        elif tokens[0] == "yield_stress":
            material.yield_stress = float(tokens[1])
        elif tokens[0] == "poisson-factor":
            material.poisson_factor = float(tokens[1])
        elif tokens[0] == "density":
            material.density = float(tokens[1])
    return material


def load_load_case(file):
    f = open("loadcases/%s.case" % file, 'r')
    lines = f.readlines()
    f.close()
    return parse_load_case(lines)


def parse_load_case(lines):
    load_case = structure.LoadCase()
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if tokens[0] == "wing":
            load_case.wing = load_wing(tokens[1])
        elif tokens[0] == "step":
            load_case.step = float(tokens[1])
        elif tokens[0] == "load_factor":
            load_case.load_factor = float(tokens[1])
        elif tokens[0] == "velocity":
            load_case.velocity = float(tokens[1])
        elif tokens[0] == "air_density":
            load_case.density = float(tokens[1])
        elif tokens[0] == "aircraft_weight":
            load_case.aircraft_weight = float(tokens[1])
        elif tokens[0] == "limit_deflection":
            load_case.limit_deflection = float(tokens[1])
        elif tokens[0] == "limit_twist":
            load_case.limit_twist = float(tokens[1])
    import numpy
    import wingloader
    load_case.range = numpy.arange(load_case.wing.wing_box.start_y, load_case.wing.wing_box.end_y, load_case.step)
    wingloader.load_wing_properties(load_case, load_case.wing)
    return load_case


def load_stringer_type(file):
    f = open("stringers/%s.stri" % file, 'r')
    lines = f.readlines()
    f.close()
    return parse_stringer_type(lines)


def parse_stringer_type(lines):
    stringer_type = structure.StringerType()
    for line in lines:
        tokens = [i.strip() for i in line.split(':')]
        if tokens[0] == "name":
            stringer_type.name = tokens[1]
        elif tokens[0] == "area":
            stringer_type.area = util.GeometryFunction(tokens[1])
        elif tokens[0] == "centroid_x":
            stringer_type.centroid_x = util.GeometryFunction(tokens[1])
        elif tokens[0] == "centroid_z":
            stringer_type.centroid_z = util.GeometryFunction(tokens[1])
        elif tokens[0] == "moi_xx":
            stringer_type.moi_xx = util.GeometryFunction(tokens[1])
        elif tokens[0] == "moi_zz":
            stringer_type.moi_zz = util.GeometryFunction(tokens[1])
    return stringer_type


def get_stringer_type(name):
    if len(stringer_types) == 0:
        init_stringer_types()
    for stringer_type in stringer_types:
        if stringer_type.name == name:
            return stringer_type
    return None


def init_stringer_types():
    import os
    for root, dirs, files in os.walk("stringers"):
        for file in files:
            if file.endswith(".stri"):
                stringer_types.append(load_stringer_type(file.split('.')[0]))


def get_material(name):
    if len(materials) == 0:
        init_material()
    for material in materials:
        if material.name == name:
            return material
    return None


def init_material():
    import os
    for root, dirs, files in os.walk("materials"):
        for file in files:
            if file.endswith(".mat"):
                materials.append(load_material(file.split('.')[0]))
