# y back block: back ends of the y rods and the 608 bearing for the y screw
from argus.geo import *
from argus.spec import F, P, pat
from parts.y_axis.layout import YSX, YSZ, Z1, YT

META = dict(name='Y back block', group='X', layer=3, sub='Y rails', step=5, color='xstage', orient='ymax',
            note='Holds the back ends of both Y rods and the 608 bearing for the Y screw.',
            hw={'M3x16 screw': 2, 'M3 heat-set insert': 2, 'M3x6 set screw': 2})


def build():
    bb = fuse(box(-50, 50, 45, 55, Z1, YT), box(50, 84, 45, 55, Z1, 61))
    cuts = [cyl(P['rod_bore_d'] / 2, (xx, 44.9, zz), (xx, 53, zz)) for xx, zz in pat('y_rods')]
    cuts += [ins((xx, 49, YT), '-z', 7.5) for xx, _ in pat('y_rods')]
    w = F.bearing_608.w
    cuts += [cyl(P['bearing_seat_d'] / 2, (YSX, 44.9, YSZ), (YSX, 45 + w + 0.2, YSZ)), cyl(5, (YSX, 45 + w, YSZ), (YSX, 55.1, YSZ))]
    cuts += [bolt_v(x, y, YT, Z1, cb_depth=12) for x, y in pat('x_carriage_to_y_blocks', only=[2, 3])]
    return cut(bb, *cuts)
