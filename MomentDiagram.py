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
    val, err = integrate.quad(f, y, 14.62, wing)
    if y <= wing.eng_pos:
        return val - wing.eng_weight * (wing.eng_pos - y)
    else:
        return val


def f(y, wing):
    return wing.lift(y) * y
