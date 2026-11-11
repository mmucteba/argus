# right x end block: both x rods and the 608 bearing for the free screw end
from argus.geo import *
from argus.spec import pat
from parts.x_axis.layout import SY, SZ, R

META = dict(name='X end block R', group='F', layer=2, sub='X rails', step=3, color='frame', orient='xmax',
            note='Holds both X rods and the 608 bearing for the free end of the X screw (replaces the out of stock KP08).',
            hw={'Wood screw 4x20': 4, 'M3 heat-set insert': 2, 'M3x6 set screw': 2})


def build():
    rb = fuse(box(R, R + 14, -54, 58, 0, 30), box(R, R + 14, 57, 84, 0, 38))
    base = [(R + 7, -20), (R + 7, 20), (R + 7, -50), (R + 7, 80)]
    cuts = [cyl(4.05, (R - 0.1, yy, zz), (R + 10, yy, zz)) for yy, zz in pat('x_rods')]
    cuts += [ins((R + 5, yy, 30), '-z', 5.8) for yy, _ in pat('x_rods')]
    cuts += [cyl(11.08, (R - 0.1, SY, SZ), (R + 7.2, SY, SZ)), cyl(5, (R + 7, SY, SZ), (R + 10, SY, SZ))]
    cuts += [wood_hole(x, y, 30, 0, cb_to=8) for x, y in base[:3]] + [wood_hole(R + 7, 80, 38, 0, cb_to=10)]
    return cut(rb, *cuts), [(x, y, 'X end block R') for x, y in base]
