# z rods, lm8uu, m4 focus screw, 28byj-48
from argus.geo import *
from argus.catalog import lm8uu
from argus.spec import P, pat
from parts.column.layout import ZY, FZC


def add_bought(add):
    for x, y in pat('z_rods'):
        add('Z rod', cyl(4, (x, y, 110), (x, y, 210)), 'F', 5, 'mech', 'Column and focus', 8, 'steel',
            density=P['rho_steel'], buy='rod', note='8 mm rod cut to 100 mm')
    for x, y in pat('z_rods'):
        add('LM8UU (Z)', lm8uu((x, y, FZC), 'z'), 'Z', 5, 'mech', 'Column and focus', 8, 'steel', mass=14, buy='LM8UU')
    sx, sy = pat('focus_drive')[0]
    add('M4 focus screw', cyl(2, (sx, sy, 175), (sx, sy, 236)), 'F', 5, 'mech', 'Column and focus', 8, 'steel',
        density=P['rho_steel'], buy='M4 rod', note='M4 x 0.7 threaded rod cut to 61 mm; 700 um per turn',
        hw={'M4 nut': 2, 'M4 washer': 1})
    mx, my = pat('focus_drive')[1]
    bx = pat('byj_mount')[0][0]
    byj = fuse(cyl(14, (bx, ZY, 224), (bx, ZY, 243)), box(bx - 17.5, bx + 17.5, ZY - 3.5, ZY + 3.5, 224, 225),
               cyl(4.5, (mx, my, 222.5), (mx, my, 224)), cyl(2.5, (mx, my, 214.5), (mx, my, 222.5)))
    add('28BYJ-48 focus motor', byj, 'F', 5, 'elec', 'Column and focus', 8, 'motor', mass=37, buy='BYJ',
        note='5 V geared stepper; 0.17 um of focus per half-step; driven from the CNC shield Z slot after the bipolar mod')
