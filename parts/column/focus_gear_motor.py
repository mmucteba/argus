# focus gear on the 28byj-48 shaft, double-d bore
from argus.geo import *
from argus.spec import pat
from parts.column.layout import GEAR_Z

META = dict(name='Focus gear (motor)', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmin',
            note='Module 1, 20 teeth, double-D bore for the 28BYJ-48 shaft (5 mm, 3 mm across flats)')


def build():
    gx, gy = pat('focus_drive')[1]
    g = spur_gear(1.0, 20, 6.0)
    dflat = cut(cyl(2.55, (0, 0, -0.1), (0, 0, 6.1)), box(-3, 3, 1.55, 3, -0.2, 6.2), box(-3, 3, -3, -1.55, -0.2, 6.2))
    return cut(g, dflat).rotate(V(0, 0, 0), V(0, 0, 1), 9).translate(V(gx, gy, GEAR_Z))
