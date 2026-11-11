# led tower: holds heatsink, led card and diffuser on the optical axis
from argus.geo import *
from argus.spec import P, IF

META = dict(name='LED tower', group='F', layer=1, sub='Light source', step=2, color='frame', orient='zmin',
            note='Holds heatsink, LED and diffuser on the optical axis. Wire exits through the side slot. Print in white PLA.',
            hw={'Wood screw 4x16': 3})


def build():
    zt = P['diffuser_top']
    seat = IF['diffuser_seat']
    zs, rs = seat['holes']['led_tower']['plane'], seat['d'] / 2
    t = fuse(cyl(16.5, (0, 0, 0), (0, 0, zt)), cyl(25, (0, 0, 0), (0, 0, 3)))
    t = cut(t, cyl(14.6, (0, 0, 3), (0, 0, 18.4)), cone(14.6, 13, (0, 0, 18.39), (0, 0, 20.01)), cyl(13, (0, 0, 20), (0, 0, zs + 0.1)),
            cyl(rs, (0, 0, zs), (0, 0, zt + 0.1)), box(10, 18, -3, 3, 3, 9))
    base = [(21 * math.cos(math.radians(a)), 21 * math.sin(math.radians(a))) for a in (90, 210, 330)]
    for x, y in base:
        t = t.cut(wood_hole(x, y, 3, 0))
    return t, [(x, y, 'LED tower') for x, y in base]
