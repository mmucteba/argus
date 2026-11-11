# y endstop flag: thin vane on the y carriage that enters the y sensor at y-
from argus.geo import *
from argus.spec import pat
from parts.y_axis.layout import C1

META = dict(name='Y endstop flag', group='Y', layer=3, sub='Y drive', step=6, color='ystage', orient='xmin',
            note='Thin vane that enters the Y sensor at the Y- end. Print on its side.', hw={'M3x8 screw': 1})


def build():
    (fx, fy), = pat('y_flag')
    flag = fuse(box(fx - 6, fx + 6, fy - 4, fy + 4, C1, C1 + 2), box(fx - 0.75, fx + 0.75, fy - 18, fy - 2, C1 + 1, C1 + 6))
    return cut(flag, cyl(1.7, (fx, fy, C1 - 0.1), (fx, fy, C1 + 2.1)))
