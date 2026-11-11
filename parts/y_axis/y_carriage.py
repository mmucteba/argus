# y carriage: rides the y rods on 4 lm8uu, carries the slide holder
from argus.geo import *
from argus.catalog import t8_mount_holes
from argus.spec import P, pat
from parts.y_axis.layout import YSX, YSZ, C0, C1

META = dict(name='Y carriage', group='Y', layer=3, sub='Y rails', step=5, color='ystage', orient='zmax',
            note='4 bearing saddles underneath, nut bracket on the right, 3 levelling inserts. Print upside down.',
            hw={'Zip tie 2.5 mm': 8, 'M3 heat-set insert': 4})


def build():
    yc = box(-56, 56, -28, 28, C0, C1)
    voids = [box(-29.5, 29.5, -14.5, 14.5, C0 - 1, C1 + 1)]
    for xx, zz in pat('y_rods'):
        for yb in (-P['yb_y'], P['yb_y']):
            blk, bore = saddle((xx, yb, zz), 'y', 24, 12, '-z', plate_face=C0 + 0.5)
            yc = yc.fuse(blk)
            voids.append(bore)
            voids += ziptie_slots((xx, yb, zz), 'y', '-z', zz - 2, C1 + 1)
    yc = yc.fuse(box(56, 80, -3, 3, 35, C1)).fuse(box(50, 80, -9, -3, C0, C1))
    voids += t8_mount_holes('y', -3, 3, YSX, YSZ)
    voids += [ins((x, y, C1), '-z', 6.2) for x, y in pat('levelling')] + [ins((x, y, C1), '-z', 6.2) for x, y in pat('y_flag')]
    return cut(yc, *voids)
