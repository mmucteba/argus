# lens clamp: split collar for the zoom lens barrel, screwed to the focus carriage
from argus.geo import *
from argus.spec import F, P, pat

META = dict(name='Lens clamp', group='Z', layer=5, sub='Optics', step=9, color='zstage', orient='zmin',
            note='Split collar for the 39 mm lens barrel, two M3 bolts close the slit. Screw it to the focus carriage first '
                 'through the bore, then slide the lens in. The lens can slide about 10 mm either way to set the height.',
            hw={'M3x16 screw': 4, 'M3 nut': 2})


def build():
    c0, c1 = 148.0, 192.0
    rb = P['lens_r'] + 0.2
    tc = fuse(tube(24.5, rb, (0, 0, c0), (0, 0, c1)), box(-10, 10, 22, 62, c0, c1), box(-7, 7, -31, -22.5, c0, c1))
    rc, nut = P['m3_clear_d'] / 2, F.m3_nut
    return cut(tc, box(-0.75, 0.75, -31.1, -18, c0 - 0.1, c1 + 0.1),
               *[cyl(rc, (-7.1, -26.75, z), (7.1, -26.75, z)) for z in (156, 184)],
               *[hexprism(nut.af + 0.2, nut.h + 0.2, (-7.01, -26.75, z), 'x') for z in (156, 184)],
               *[cyl(rc, (x, 18, z), (x, 62.1, z)).fuse(cyl(3.2, (x, 18, z), (x, 52, z))) for x, z in pat('focus_to_lens_clamp')])
