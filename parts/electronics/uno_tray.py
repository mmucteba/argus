# uno tray: standoffs for the uno + cnc shield, zip-tie slots for the small boards
from argus.geo import *
from argus.spec import pat

META = dict(name='Uno tray', group='F', layer=0, sub='Electronics', step=11, color='frame', orient='zmin',
            note='Standoffs for the Uno + CNC shield, zip-tie slots for the LED driver, buck module and DC jack.',
            hw={'Wood screw 4x16': 4, 'M3 heat-set insert': 4, 'M3x6 screw': 4, 'Zip tie 2.5 mm': 3})


def build():
    tr = box(-132, 12, -114, -58, 0, 3)
    for x, y in pat('uno_mount'):
        tr = tr.fuse(cyl(3.6, (x, y, 3), (x, y, 9)))
    base = [(-128, -110), (-128, -62), (8, -110), (8, -62)]
    tr = cut(tr, *[ins((x, y, 9), '-z', 6.2) for x, y in pat('uno_mount')], *[wood_hole(x, y, 3, 0) for x, y in base],
             *[box(x - 1, x + 1, y - 1.8, y + 1.8, -0.1, 3.1) for x in (-50, -30, -10) for y in (-100, -72)])
    return tr, [(x, y, 'Uno tray') for x, y in base]
