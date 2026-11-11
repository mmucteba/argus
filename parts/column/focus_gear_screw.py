# focus gear on the m4 screw, m4 nut pressed in
from argus.geo import *
from argus.spec import pat
from parts.column.layout import GEAR_Z

META = dict(name='Focus gear (screw)', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmin',
            note='Module 1, 20 teeth; M4 nut pressed into the bottom, locked by a second nut on top')


def build():
    gx, gy = pat('focus_drive')[0]
    g = spur_gear(1.0, 20, 6.0)
    return cut(g, cyl(2.2, (0, 0, -0.1), (0, 0, 6.1)), hexprism(7.2, 3.4, (0, 0, -0.01))).translate(V(gx, gy, GEAR_Z))
