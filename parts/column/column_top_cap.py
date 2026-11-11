# column top cap: upper z rod ear, fits over the column top
from argus.geo import *
from argus.spec import P, pat
from parts.column.layout import ZY

META = dict(name='Column top cap', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmax',
            note='Upper Z rod ear. Its pocket fits over the column top so the rod bores line up with the lower ear. '
                 'Printed flat so the rod bores come out round.',
            hw={'M3x16 screw': 2, 'M3 heat-set insert': 4, 'M3x6 set screw': 2})


def build():
    cap = box(-30, 30, 66, 136, 196, 210)
    return cut(cap, box(-25.2, 25.2, 91.8, 132.2, 195.9, 200),
               *[cyl(P['rod_bore_d'] / 2, (x, y, 195.9), (x, y, 210.1)) for x, y in pat('z_rods')],
               *[ins((x, 66, 203), '+y', 6.0) for x, _ in pat('z_rods')],
               cyl(2.4, (0, ZY, 195.9), (0, ZY, 210.1)),   # loose fit for the m4 rod
               *[ins((x, y, 210), '-z', 6.0) for x, y in pat('cap_to_bracket')],
               *[bolt_v(x, y, 210, 200, cb_depth=3.2) for x, y in pat('column_to_cap')])
