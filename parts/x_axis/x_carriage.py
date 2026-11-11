# x carriage: rides the x rods on 4 lm8uu, carries the y axis, nut bracket at the back, endstop vane
from argus.geo import *
from argus.catalog import t8_mount_holes
from argus.spec import P, pat
from parts.x_axis.layout import SY, SZ, EY

META = dict(name='X carriage', group='X', layer=2, sub='X rails', step=3, color='xstage', orient='zmax',
            note='One piece: 4 bearing saddles underneath, nut bracket at the back, endstop vane, light opening 66 x 62 mm. '
                 'Print upside down, saddles face up, no supports.',
            hw={'Zip tie 2.5 mm': 8, 'M3 heat-set insert': 4})


def build():
    z0, z1 = P['xc_z']
    xc = box(-50, 50, -56, 56, z0, z1)
    voids = [box(-33, 33, -31, 31, z0 - 1, z1 + 1)]
    for xb in (-P['xb_x'], P['xb_x']):
        for yy, zz in pat('x_rods'):
            blk, bore = saddle((xb, yy, zz), 'x', 26, 11.5, '-z', plate_face=z0 + 0.5)
            xc = xc.fuse(blk)
            voids.append(bore)
            voids += ziptie_slots((xb, yy, zz), 'x', '-z', zz - 2, z1 + 1)
    # nut bracket at the back for the x screw
    xc = xc.fuse(box(-3, 3, 56, 83, 12, z1)).fuse(box(-9, -3, 50, 62, z0, z1))
    voids += t8_mount_holes('x', -3, 3, SY, SZ)
    # endstop vane
    xc = xc.fuse(box(-44, -38, EY - 0.75, EY + 0.75, 15.5, z0 + 0.5))
    voids += [ins((x, y, z1), '-z', 5.7) for x, y in pat('x_carriage_to_y_blocks')]
    return cut(xc, *voids)
