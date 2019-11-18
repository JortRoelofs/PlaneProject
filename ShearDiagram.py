from scipy import integrate
import Wing


def calcShearValues(wing):
    ylst = []
    index = 0
    for y in Wing.stdrange:
        ylst.append(shear(wing, y))
        index += 1
    return Wing.stdrange, ylst


# noinspection PyTupleAssignmentBalance
def shear(wing, y):
    val, err = integrate.quad(wing.lift, y, Wing.wing_max)
    if y <= wing.eng_y:
        return val - wing.eng_weight
    else:
        return val
