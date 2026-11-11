# overview camera (placeholder) and its led
from argus.geo import *
from argus.spec import P


def add_bought(add):
    oc = P['overview']
    cam = fuse(box(oc['x'] - 12.5, oc['x'] + 12.5, -12, 12, 183, 184),
               box(oc['x'] - 4.25, oc['x'] + 4.25, -4.25, 4.25, oc['z_lens'], 183),
               box(oc['x'] - 3, oc['x'] + 3, -10, 10, 184, 186))
    add('Overview camera (USB, tbd)', cam, 'F', 6, 'elec', 'Overview camera', 10, 'pcb', mass=4, buy='cam3',
        note='placeholder: the Pi has one camera port (HQ), so the overview camera will be a USB module; '
             'the arm gets redesigned when we pick it')
    add('Overview LED 5 mm', fuse(cyl(2.5, (oc['x'], 18, 184), (oc['x'], 18, 196)), cyl(2.9, (oc['x'], 18, 196), (oc['x'], 18, 197))),
        'F', 6, 'elec', 'Overview camera', 10, 'led', mass=0.5, buy='led5', note='lights the slide from above for the overview photo')
