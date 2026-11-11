# focus gear on the m4 screw, m4 nut pressed in
from argus.geo import *
from argus.spec import F, P, pat
from parts.column.layout import GEAR_Z

META = dict(name='Focus gear (screw)', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmin',
            note='Module 1, 20 teeth; M4 nut pressed into the bottom, locked by a second nut on top')


def build():
    gx, gy = pat('focus_drive')[0]
    g = spur_gear(1.0, 20, 6.0)
    nut = F.m4_nut
    return cut(g, cyl(P['m4_clear_d'] / 2, (0, 0, -0.1), (0, 0, 6.1)),
               hexprism(nut.af + 0.2, nut.h + 0.2, (0, 0, -0.01))).translate(V(gx, gy, GEAR_Z))
