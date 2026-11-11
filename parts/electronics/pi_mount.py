# pi mount: four standoffs for the raspberry pi 3b+
from argus.geo import *
from argus.spec import P, pat

META = dict(name='Pi mount', group='F', layer=0, sub='Electronics', step=11, color='frame', orient='zmin',
            note='Four standoffs for the Pi 3B+ (58 x 49 mm hole pattern, M2.5 screws tap into 2.2 mm holes).',
            hw={'Wood screw 4x16': 4, 'M2.5x8 screw': 4})


def build():
    pm = box(37, 127, 88, 148, 0, 3)
    for x, y in pat('pi_mount'):
        pm = pm.fuse(cyl(3, (x, y, 3), (x, y, 8)))
    base = [(122, 92), (122, 144), (42, 146), (104, 146)]
    pm = cut(pm, *[cyl(P['m25_tap_d'] / 2, (x, y, 3), (x, y, 8.1)) for x, y in pat('pi_mount')], *[wood_hole(x, y, 3, 0) for x, y in base])
    return pm, [(x, y, 'Pi mount') for x, y in base]
