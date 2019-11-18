from scipy import integrate
import Wing

def calcTorqueValues(wing):
    ylst = []
    index = 0
    for y in Wing.stdrange:
        ylst.append(torque(wing, y))
        index += 1
    return Wing.stdrange, ylst


# noinspection PyTupleAssignmentBalance
def torque(wing, y):
    val, err = integrate.quad(f, y, Wing.wing_max, wing)
    if y <= wing.eng_y:
        return val + wing.eng_thrust * wing.eng_z
    else:
        return val


def f(y, wing):
    return wing.lift(y) * (wing.Cp(y) - 0.4 * wing.X(y))
