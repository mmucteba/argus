# focus motor bracket: sits on the top cap over the gears, carries the 28byj-48 upside down
from argus.geo import *
from argus.spec import F, pat

META = dict(name='Focus motor bracket', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmax',
            note='Sits on the upper ear over the gears and carries the 28BYJ-48 upside down.',
            hw={'M3x16 screw': 2, 'M4x8 screw': 2, 'M4 nut': 2})


def build():
    br = fuse(box(-14, 46, 54, 98, 221, 224), box(-26, -14, 88, 92, 210, 221.1), box(14, 26, 88, 92, 210, 221.1))
    (sx, sy), (mx, my) = pat('focus_drive')
    b = F.byj48
    return cut(br, cyl(5, (sx, sy, 220.9), (sx, sy, 224.1)), cyl((b.boss_d + 0.2) / 2, (mx, my, 220.9), (mx, my, 224.1)),
               *[cyl(b.ear_hole_d / 2, (x, y, 220.9), (x, y, 224.1)) for x, y in pat('byj_mount')],
               *[bolt_v(x, y, 224, 210) for x, y in pat('cap_to_bracket')])
