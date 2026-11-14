# focus gear on the 28byj-48 shaft, double-d bore
from argus.geo import *
from argus.spec import F, pat
from parts.column.layout import GEAR_Z

META = dict(name='Focus gear (motor)', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmin',
            note='Module 1, 20 teeth, double-D bore for the 28BYJ-48 shaft (5 mm, 3 mm across flats)')

MOD, THICK = 1.0, 6.0              # gear module and thickness same as the screw gear
FIT = 0.1                          # bore allowance on the shaft for a snug press fit


def build():
    (sx, _), (gx, gy) = pat('focus_drive')
    teeth = round((gx - sx) / MOD)  # 1 to 1 pair so centre distance is module times teeth
    g = spur_gear(MOD, teeth, THICK)
    b = F.byj48
    rs, fl = (b.shaft_d + FIT) / 2, (b.shaft_flats + FIT) / 2
    dflat = cut(cyl(rs, (0, 0, -0.1), (0, 0, THICK + 0.1)),
                box(-3, 3, fl, 3, -0.2, THICK + 0.2), box(-3, 3, -3, -fl, -0.2, THICK + 0.2))
    # half a tooth pitch so a gap faces the screw gear tooth on the centre line
    return cut(g, dflat).rotate(V(0, 0, 0), V(0, 0, 1), 180 / teeth).translate(V(gx, gy, GEAR_Z))
