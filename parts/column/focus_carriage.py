# focus carriage: rides the z rods on 2 lm8uu, m4 nut on top, carries the lens clamp
from argus.geo import *
from argus.spec import F, pat
from parts.column.layout import ZY, FZ0, FZ1, FZC

META = dict(name='Focus carriage', group='Z', layer=5, sub='Column and focus', step=8, color='zstage', orient='ymin',
            note='Rides the Z rods on 2 LM8UU; M4 nut pressed in on top; the extension spring hooks on the lug underneath so '
                 'the screw is always loaded one way (no Z backlash).',
            hw={'Zip tie 2.5 mm': 4, 'M3 heat-set insert': 2, 'M4 nut': 1, 'Extension spring 5x20': 1})


def build():
    fc = box(-30, 30, 62, 68, FZ0, FZ1)
    voids = []
    for x, y in pat('z_rods'):
        blk, bore = saddle((x, y, FZC), 'z', 26, 12, '+y', plate_face=67.5)
        fc = fc.fuse(blk)
        voids.append(bore)
        voids += ziptie_slots((x, y, FZC), 'z', '+y', 61.9, y - 2)
    fc = fc.fuse(box(-6, 6, 66, 82, 183, FZ1)).fuse(box(8, 12, 64, 70, 145, FZ0 + 1))
    nut = F.m4_nut
    af, nh = nut.af + 0.2, nut.h + 0.2
    voids += [hexprism(af, nh, (0, ZY, FZ1 - nh)), cyl(2.3, (0, ZY, 182.9), (0, ZY, FZ1 + 0.1)),
              cyl(1.2, (7.9, 67, 147.5), (12.1, 67, 147.5))]
    voids += [ins((x, 62, z), '+y', 6.0) for x, z in pat('focus_to_lens_clamp')]
    return cut(fc, *voids)
