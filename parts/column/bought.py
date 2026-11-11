# z rods, lm8uu, m4 focus screw, 28byj-48
from argus.geo import *
from argus.catalog import lm8uu
from argus.spec import F, P, pat
from parts.column.layout import ZY, FZC


def add_bought(add):
    for x, y in pat('z_rods'):
        add('Z rod', cyl(F.rod_8mm.d / 2, (x, y, 110), (x, y, 210)), 'F', 5, 'mech', 'Column and focus', 8, 'steel',
            density=P['rho_steel'], buy='rod', note='8 mm rod cut to 100 mm')
    for x, y in pat('z_rods'):
        add('LM8UU (Z)', lm8uu((x, y, FZC), 'z'), 'Z', 5, 'mech', 'Column and focus', 8, 'steel', mass=14, buy='LM8UU')
    sx, sy = pat('focus_drive')[0]
    add('M4 focus screw', cyl(F.m4_rod.d / 2, (sx, sy, 175), (sx, sy, 236)), 'F', 5, 'mech', 'Column and focus', 8, 'steel',
        density=P['rho_steel'], buy='M4 rod', note='M4 x 0.7 threaded rod cut to 61 mm; 700 um per turn',
        hw={'M4 nut': 2, 'M4 washer': 1})
    mx, my = pat('focus_drive')[1]
    bx = pat('byj_mount')[0][0]
    b = F.byj48
    zb, zs = 224 - b.boss_h, 224 - b.boss_h - b.shaft_len
    byj = fuse(cyl(b.body_d / 2, (bx, ZY, 224), (bx, ZY, 224 + b.body_h)),
               box(bx - b.ear_spacing / 2, bx + b.ear_spacing / 2, ZY - 3.5, ZY + 3.5, 224, 225),
               cyl(b.boss_d / 2, (mx, my, zb), (mx, my, 224)), cyl(b.shaft_d / 2, (mx, my, zs), (mx, my, zb)))
    add('28BYJ-48 focus motor', byj, 'F', 5, 'elec', 'Column and focus', 8, 'motor', mass=37, buy='BYJ',
        note='5 V geared stepper; 0.17 um of focus per half-step; driven from the CNC shield Z slot after the bipolar mod')
