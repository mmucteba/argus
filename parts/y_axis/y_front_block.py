# y front block: front ends of the y rods, the y motor and the y endstop sensor
from argus.geo import *
from argus.catalog import nema_holes
from argus.spec import pat
from parts.y_axis.layout import YSX, YSZ, Z1, YT

META = dict(name='Y front block', group='X', layer=3, sub='Y rails', step=5, color='xstage', orient='ymin',
            note='Holds the front ends of both Y rods, the Y motor and the Y endstop sensor. Print on its front face.',
            hw={'M3x16 screw': 2, 'M3 heat-set insert': 4, 'M3x6 set screw': 2})


def build():
    fb = fuse(box(-50, 50, -66, -45, Z1, YT), box(47, 89, -66, -60, 25, 69), box(56, 80, -60, -45, Z1, 36),
              box(47, 51, -60, -45, Z1, 60), box(85, 89, -60, -45, Z1, 60))
    cuts = [cyl(4.05, (xx, -44.9, zz), (xx, -55, zz)) for xx, zz in pat('y_rods')]
    cuts += [ins((xx, -50, YT), '-z', 7.5) for xx, _ in pat('y_rods')]
    cuts += nema_holes('y', -66, 6, YSX, YSZ)
    cuts += [bolt_v(x, y, YT, Z1, cb_depth=12) for x, y in pat('x_carriage_to_y_blocks', only=[0, 1])]
    cuts += [ins((x, y, YT), '-z') for x, y in pat('y_endstop_sensor')]
    return cut(fb, *cuts)
