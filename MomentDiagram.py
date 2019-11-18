from scipy import integrate
import Wing


def calcMomentValues(wing):
    ylst = []
    index = 0
    for y in Wing.stdrange:
        ylst.append(moment(wing, y))
        index += 1
    return Wing.stdrange, ylst


# noinspection PyTupleAssignmentBalance
def moment(wing, y):
    val, err = integrate.quad(f, y, Wing.wing_max, wing)
    if y <= wing.eng_y:
        return val - wing.eng_weight * (wing.eng_y - y)
    else:
        return val


def f(y, wing):
    return wing.lift(y) * y
