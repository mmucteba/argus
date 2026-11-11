# heatsink, led and diffuser
from argus.geo import *
from argus.spec import P


def add_bought(add):
    zt = P['diffuser_top']
    add('Heatsink', box(-10, 10, -10, 10, 3, 11), 'F', 1, 'mech', 'Light source', 2, 'alu', mass=12, buy='heatsink',
        note='20 x 20 mm aluminium, LED star screwed on with 2 M3x8 and thermal paste', hw={'M3x8 screw': 2})
    add('3 W LED on star PCB', fuse(cyl(10, (0, 0, 11), (0, 0, 12.6)), cyl(3, (0, 0, 12.6), (0, 0, 15))), 'F', 1, 'elec',
        'Light source', 2, 'led', mass=2, buy='LED', note='placeholder shape: the real part is the 23 x 30 mm Robotistan LED card with its own driver, 5 V, on/off from GRBL CoolEn (A3)')
    add('Opal diffuser', cyl(13.9, (0, 0, 22), (0, 0, zt)), 'F', 1, 'mech', 'Light source', 2, 'diffuser', mass=2,
        buy='diffuser', note='28 mm disc of 3 mm opal acrylic; sets how evenly the slide is lit')
