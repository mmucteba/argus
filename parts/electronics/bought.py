# arduino uno + cnc shield, raspberry pi 3b+
from argus.geo import *
from argus.spec import F, P


def add_bought(add):
    ux, uy = P['uno_origin']
    u = F.uno
    uno = fuse(box(ux, ux + u.pcb_l, uy, uy + u.pcb_w, 9, 10.6), box(ux + 2, ux + 66, uy + 2, uy + 51, 10.6, 32))
    add('Arduino Uno + CNC Shield V3', uno, 'F', 0, 'elec', 'Electronics', 11, 'pcb', mass=60, buy='Uno',
        note='GRBL 1.1; DRV8825 on X and Y, A4988 on Z (focus)')
    px, py = P['pi_origin']
    pi = fuse(box(px, px + F.pi3b.pcb_l, py, py + F.pi3b.pcb_w, 8, 9.6), box(px + 2, px + 85, py + 30, py + 54, 9.6, 24),
              box(px + 10, px + 45, py + 10, py + 40, 9.6, 12))
    add('Raspberry Pi 3B+', pi, 'F', 0, 'elec', 'Electronics', 11, 'pcb', mass=50, buy='Pi',
        note='runs the scan: HQ camera, G-code to the Uno over USB, LED ring data, tiles to the laptop over Ethernet. '
             'Stitching and AI run on the laptop.')
