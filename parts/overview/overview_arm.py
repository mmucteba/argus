# overview arm: bolts through the column, carries the overview camera above the slide park position
from argus.geo import *
from argus.spec import P, pat

META = dict(name='Overview arm', group='F', layer=6, sub='Overview camera', step=10, color='overview', orient='zmax',
            note='Bolts through the column; carries the overview camera 113 mm above the slide and a 5 mm white LED for '
                 'reflected light.', hw={'M3x60 screw': 2, 'M3 nut': 2, 'M2x6 screw': 4})


def build():
    oc = P['overview']
    arm = fuse(box(25, 31, 98, 126, 180, 196), box(25, 82, 106, 118, 188, 196), box(68, 82, -14, 118, 188, 196),
               box(62, 88, -16, 22, 186, 196))
    return cut(arm, *[cyl(1.7, (24.9, y, z), (31.1, y, z)) for y, z in pat('column_to_overview')],
               cyl(5, (oc['x'], 0, 185.9), (oc['x'], 0, 196.1)), cyl(2.6, (oc['x'], 18, 185.9), (oc['x'], 18, 196.1)),
               *[cyl(1.0, (x, y, 185.9), (x, y, 192)) for x, y in pat('overview_camera_mount')])
