import string
import sys

from scipy import interpolate


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def load_k(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    val = [[], []]
    for line in lines:
        tokens = line.split(',')
        val[0].append(float(tokens[0]))
        val[1].append(float(tokens[1]))
    return interpolate.interp1d(val[0], val[1], kind="cubic", fill_value="extrapolate")


class GeometryFunction:

    def __init__(self, function):
        self.function = function
        for c in string.ascii_lowercase:
            if c in self.function:
                self.function = self.function.replace(c, "{%s}" % c)

    def evaluate(self, **kwargs):
        return eval(self.function.format(**kwargs))


class SkinPlate:

    def __init__(self, thickness, start_y, end_y, width, side, surface_top):
        self.thickness = thickness
        self.start_y = start_y
        self.end_y = end_y
        self.width = width
        self.side = side
        self.surface_top = surface_top
