# mass, print orientation and helpers shared by checks and exports
from cadquery import Vector as V
from argus.spec import P, META

ORIENT_TXT = META['orient_txt']


def mass_of(p):
    if p['mass'] is not None:
        return p['mass']
    vol_cm3 = p['shape'].Volume() / 1000.0
    if p['cat'] == 'printed':
        return vol_cm3 * P['rho_pla'] * P['fill_pla']
    return vol_cm3 * (p['density'] or P['rho_steel'])


def oriented(shape, key):
    # rotate a part into its print orientation and put it on the bed at z 0
    s = shape
    if key == 'zmax':
        s = s.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    elif key == 'xmin':
        s = s.rotate(V(0, 0, 0), V(0, 1, 0), -90)
    elif key == 'xmax':
        s = s.rotate(V(0, 0, 0), V(0, 1, 0), 90)
    elif key == 'ymin':
        s = s.rotate(V(0, 0, 0), V(1, 0, 0), 90)
    elif key == 'ymax':
        s = s.rotate(V(0, 0, 0), V(1, 0, 0), -90)
    bb = s.BoundingBox()
    return s.translate(V(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
