# y rods, motor, coupling, lead screw, bearing, endstop sensor, lm8uu and nut
from argus.geo import *
from argus.catalog import nema17, lm8uu, t8_nut, endstop_board
from argus.spec import F, P, pat
from parts.y_axis.layout import YSX, YSZ, YT


def add_bought(add):
    for xx, zz in pat('y_rods'):
        add('Y rod', cyl(F.rod_8mm.d / 2, (xx, -55, zz), (xx, 53, zz)), 'X', 3, 'mech', 'Y rails', 5, 'steel', density=P['rho_steel'],
            buy='rod', note='8 mm hardened rod cut to 108 mm (each 250 mm rod gives one Y rod and one Z rod)')
    add('Y motor NEMA17', nema17(-66, 'y', +1, YSX, YSZ), 'X', 3, 'elec', 'Y drive', 6, 'motor', mass=280,
        buy='NEMA17', note='same motor as X so the spare fits both; cable needs slack, it rides on the X carriage',
        hw={'M3x10 screw': 4})
    add('Y coupling', tube(F.coupling.d / 2, 2.4, (YSX, -54, YSZ), (YSX, -54 + F.coupling.length, YSZ)), 'X', 3, 'mech', 'Y drive', 6, 'alu', mass=9,
        buy='coupling')
    add('Y lead screw', cyl(F.t8_screw.d / 2, (YSX, -41.5, YSZ), (YSX, 52, YSZ)), 'X', 3, 'mech', 'Y drive', 6, 'steel',
        density=P['rho_steel'], buy='T8 screw', note='T8, cut to 94 mm from the rest of the 400 mm screw')
    bg = F.bearing_608
    add('608ZZ bearing (Y)', tube(bg.od / 2, bg.bore / 2, (YSX, 45, YSZ), (YSX, 45 + bg.w, YSZ)), 'X', 3, 'mech', 'Y drive', 6, 'steel', mass=12,
        buy='608')
    sx = sum(x for x, _ in pat('y_endstop_sensor')) / 2
    sy = pat('y_endstop_sensor')[0][1]
    add('Y endstop sensor', endstop_board(sx, sy, YT, 'x'), 'X', 3, 'elec', 'Y drive', 6, 'sensor', mass=4,
        buy='endstop', hw={'M3x8 screw': 2}, note='lies on top of the Y front block; the flag on the Y carriage enters at Y-')
    for xx, zz in pat('y_rods'):
        for yb in (-P['yb_y'], P['yb_y']):
            add('LM8UU (Y)', lm8uu((xx, yb, zz), 'y'), 'Y', 3, 'mech', 'Y rails', 5, 'steel', mass=14, buy='LM8UU')
    add('T8 spring nut (Y)', t8_nut('y', 3, YSX, YSZ), 'Y', 3, 'mech', 'Y drive', 6, 'brass', mass=20,
        buy='T8 nut', hw={'M3x12 screw': 4, 'M3 nut': 4})
