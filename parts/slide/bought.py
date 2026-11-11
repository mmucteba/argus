# levelling springs, glass slide, coverslip
from argus.geo import *
from argus.spec import F, P, pat


def add_bought(add):
    c1, h0 = P['yc_z'][1], P['holder_z'][0]
    zf = P['z_focal']
    for x, y in pat('levelling'):
        add('Levelling spring', tube(3, 1.7, (x, y, c1), (x, y, h0)), 'Y', 4, 'mech', 'Slide holder', 7, 'steel', mass=0.5)
    sl, sw = P['slide_l'] / 2, P['slide_w'] / 2
    add('Glass slide', box(-sl, sl, -sw, sw, P['z_slide_bot'], zf), 'Y', 4, 'mech', 'Slide holder', 7, 'glass',
        density=P['rho_glass'], buy='slide')
    c = F.coverslip
    add('Coverslip', box(-34, -34 + c.l, -c.w / 2, c.w / 2, zf, P['z_cover_top']), 'Y', 4, 'mech', 'Slide holder', 7, 'glass',
        density=P['rho_glass'])
