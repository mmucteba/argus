# zoom lens, hq camera, led ring
from argus.geo import *
from argus.spec import P
from parts.optics.layout import LF, ZC, LR, RING_Z, RING_TOP


def add_bought(add):
    lens = fuse(cyl(LR - 1.5, (0, 0, LF), (0, 0, LF + 5)), cyl(LR, (0, 0, LF + 5), (0, 0, ZC)),
                cyl(12.6, (0, 0, ZC), (0, 0, ZC + P['lens_thread'])))
    add('Zoom lens 0.12-1.8x', lens, 'Z', 5, 'mech', 'Optics', 9, 'tube', mass=202, buy='lens',
        note=f'Waveshare 100X industrial microscope lens, C-mount, 39 x 112 mm. Zoom set to 1.8x; working distance about '
             f'{P["wd"]:.0f} mm there (listing says 55-285 mm over the zoom range), measure on arrival. NA is not published.')
    add('Zoom lens front glass', cyl(15, (0, 0, LF - 0.2), (0, 0, LF)), 'Z', 5, 'mech', 'Optics', 9, 'optic', mass=0.5)
    zs = P['z_sensor']
    hq = fuse(tube(18, 15, (0, 0, ZC), (0, 0, zs)), box(-19, 19, -19, 19, zs, zs + 1.6), box(-15, 15, -15, 15, zs + 1.6, zs + 5.6))
    add('Raspberry Pi HQ Camera', hq, 'Z', 5, 'elec', 'Optics', 9, 'pcb', mass=35, buy='HQ',
        note='IMX477 with the C-CS adapter fitted; hangs on the lens. 50 cm ribbon cable down to the Pi.')
    add('LED ring 24x WS2812', tube(43.25, 35.75, (0, 0, RING_Z), (0, 0, RING_TOP)), 'Z', 5, 'elec', 'Optics', 9, 'pcb',
        mass=6, buy='ring', note='86.5 / 71.5 mm, 24 LEDs, data from Pi GPIO10 through the 74HCT125, 5 V from the buck')
