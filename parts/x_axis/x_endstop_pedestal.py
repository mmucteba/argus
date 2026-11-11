# x endstop pedestal: optical fork board lies on top, vane on the x carriage passes through the fork
from argus.geo import *
from argus.spec import pat
from parts.x_axis.layout import EX, EY

META = dict(name='X endstop pedestal', group='F', layer=2, sub='X drive', step=4, color='frame', orient='zmin',
            note='Sensor board lies on top, long side along Y. Hole spacing 19 mm assumed; check your board and slot the holes '
                 'if needed.', hw={'Wood screw 4x16': 2, 'M3 heat-set insert': 2, 'M3x8 screw': 2})


def build():
    ped = box(EX - 8, EX + 8, EY - 26, EY + 26, 0, 10)
    base = [(EX, EY - 22), (EX, EY + 22)]
    ped = cut(ped, *[wood_hole(x, y, 10, 0) for x, y in base],
              *[ins((x, y, 10), '-z') for x, y in pat('x_endstop_sensor')])
    return ped, [(x, y, 'X endstop') for x, y in base]
