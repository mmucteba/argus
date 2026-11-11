# left x end block: both x rods and the x motor
from argus.geo import *
from argus.catalog import nema_holes
from argus.spec import pat
from parts.x_axis.layout import SY, SZ, L

META = dict(name='X end block L', group='F', layer=2, sub='X rails', step=3, color='frame', orient='xmin',
            note='Holds both X rods (parallel by print) and the X motor. Print on its outer face, rod pockets point up.',
            hw={'Wood screw 4x20': 3, 'Wood screw 4x16': 2, 'M3 heat-set insert': 2, 'M3x6 set screw': 2})


def build():
    lb = fuse(box(L - 14, L, -54, 58, 0, 30), box(L - 14, L - 8, 47, 93, 0, 47), box(L - 14, L + 6, 47, 93, 0, 6))
    base = [(L - 7, -20), (L - 7, 20), (L - 7, -50), (L + 1, 62), (L + 1, 86)]
    cuts = [cyl(4.05, (L + 0.1, yy, zz), (L - 10, yy, zz)) for yy, zz in pat('x_rods')]
    cuts += [ins((L - 5, yy, 30), '-z', 5.8) for yy, _ in pat('x_rods')]
    cuts += nema_holes('x', L - 14, 6, SY, SZ)
    cuts += [wood_hole(x, y, 30, 0, cb_to=8) for x, y in base[:3]]
    cuts += [wood_hole(x, y, 6, 0) for x, y in base[3:]]
    return cut(lb, *cuts), [(x, y, 'X end block L') for x, y in base]
