# x rods, motor, coupling, lead screw, bearing, endstop sensor, lm8uu and nut
from argus.geo import *
from argus.catalog import nema17, lm8uu, t8_nut, endstop_board
from argus.spec import P, pat
from parts.x_axis.layout import SY, SZ, L, R, EX, EY, ROD_X, CPL


def add_bought(add):
    for yy, zz in pat('x_rods'):
        add('X rod', cyl(4, (ROD_X[0], yy, zz), (ROD_X[1], yy, zz)), 'F', 2, 'mech', 'X rails', 3, 'steel',
            density=P['rho_steel'], buy='rod', note=f'8 mm hardened rod cut to {ROD_X[1] - ROD_X[0]:.0f} mm from 250')
    add('X motor NEMA17', nema17(L - 14, 'x', +1, SY, SZ), 'F', 2, 'elec', 'X drive', 4, 'motor', mass=280,
        buy='NEMA17', note='17HS4401, 1.7 A, 40 N cm holding; mounted from inside with 4 M3x10', hw={'M3x10 screw': 4})
    add('X coupling', tube(9.5, 2.4, (CPL[0], SY, SZ), (CPL[1], SY, SZ)), 'F', 2, 'mech', 'X drive', 4, 'alu', mass=9,
        buy='coupling', note='5 mm motor shaft to 8 mm screw')
    xs0, xs1 = CPL[1] - 12.5, R + 7
    add('X lead screw', cyl(4, (xs0, SY, SZ), (xs1, SY, SZ)), 'F', 2, 'mech', 'X drive', 4, 'steel',
        density=P['rho_steel'], buy='T8 screw', note=f'T8, 8 mm lead, cut to {xs1 - xs0:.0f} mm from the 400 mm screw')
    add('608ZZ bearing (X)', tube(11, 4, (R, SY, SZ), (R + 7, SY, SZ)), 'F', 2, 'mech', 'X drive', 4, 'steel', mass=12,
        buy='608', note='22 x 8 x 7, pressed into the right end block')
    add('X endstop sensor', endstop_board(EX, EY, 10, 'y'), 'F', 2, 'elec', 'X drive', 4, 'sensor', mass=4,
        buy='endstop', note='optical fork (TCST2103 type); triggers at the X- end of travel for homing')
    for xb in (-P['xb_x'], P['xb_x']):
        for yy, zz in pat('x_rods'):
            add('LM8UU (X)', lm8uu((xb, yy, zz), 'x'), 'X', 2, 'mech', 'X rails', 3, 'steel', mass=14, buy='LM8UU')
    add('T8 spring nut (X)', t8_nut('x', 3, SY, SZ), 'X', 2, 'mech', 'X drive', 4, 'brass', mass=20, buy='T8 nut',
        note='anti-backlash nut; 4 holes are 0.4 mm oversize so it can float into line before tightening',
        hw={'M3x12 screw': 4, 'M3 nut': 4})
