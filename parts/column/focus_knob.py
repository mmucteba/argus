# focus knob on top of the m4 screw
from argus.geo import *
from argus.spec import pat

META = dict(name='Focus knob', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmin',
            note='Knurled, M4 nut pressed in. 10 um of focus is about 5 degrees of rotation.')


def build():
    sx, sy = pat('focus_drive')[0]
    kn = cyl(11, (0, 0, 0), (0, 0, 10))
    kn = cut(kn, cyl(2.2, (0, 0, -0.1), (0, 0, 10.1)), hexprism(7.2, 3.4, (0, 0, -0.01)),
             *[cyl(1.4, (11 * math.cos(a), 11 * math.sin(a), 1), (11 * math.cos(a), 11 * math.sin(a), 10.1))
               for a in [2 * math.pi * k / 18 for k in range(18)]])
    return kn.translate(V(sx, sy, 225))
