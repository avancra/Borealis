from math import sin, cos, radians


def geo_monor(bragg):
    return 90 - bragg


def geo_tuber(bragg):
    return 2 * (90 - bragg)


def geo_monox(bragg):
    pos_theo = 500 * sin(radians(bragg))
    return pos_theo


def geo_tubex(bragg):
    # correction =  -9.177849451E-03*bragg*bragg*bragg + 2.007762068E+00*bragg*bragg - 1.428034314E+02*bragg + 3.259040690E+03
    correction = 0
    pos_theo = (2 * 500 * (sin(radians(bragg)) *
                           cos(radians(bragg)) *
                           cos(radians(bragg))) +
                correction)

    return pos_theo


def geo_tubey(bragg):
    correction = 0
    # correction = 1.944939468E-01*bragg*bragg - 3.256010364E+01*bragg + 1.367028138E+03
    pos_theo = (2 * 500 * (sin(radians(bragg)) *
                           sin(radians(bragg)) *
                           cos(radians(bragg))) +
                correction)
    return pos_theo