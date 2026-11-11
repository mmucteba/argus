# ring light holder: push-fit sleeve on the lens front, cone carries the led ring
from argus.geo import *
from argus.spec import P
from parts.optics.layout import LF, LR, RING_Z, RING_TOP

META = dict(name='Ring light holder', group='Z', layer=5, sub='Optics', step=9, color='zstage', orient='zmin',
            note=f'Push-fit on the lens front; a 52 degree cone carries the 86.5 mm LED ring {RING_Z - P["z_focal"]:.0f} mm '
                 f'above the slide, so the light hits printed targets at about '
                 f'{math.degrees(math.atan(39.5 / (RING_Z - P["z_focal"]))):.0f} degrees and glare stays out of the lens. '
                 'Prints as assembled, no supports.')


def build():
    rb = LR + 0.2
    pt = RING_TOP + 2.5
    plate = tube(44.5, 34.0, (0, 0, RING_TOP), (0, 0, pt))
    shell = cut(cone(36.5, 22.3, (0, 0, pt - 0.01), (0, 0, pt + 18)), cone(34.5, 20.3, (0, 0, pt - 0.02), (0, 0, pt + 18.01)))
    zj = 126.0
    sleeve = cut(cyl(23.5, (0, 0, zj), (0, 0, LF + 20)), cone(23.4, rb, (0, 0, zj - 0.01), (0, 0, zj + 3.7)),
                 cyl(rb, (0, 0, zj + 3.69), (0, 0, LF + 20.1)))
    return fuse(plate, shell, sleeve).clean()
