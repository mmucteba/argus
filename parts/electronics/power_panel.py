# power panel: dc jack, switch, fuse, buck and the level shifter in one place at the back left
# placeholder plate until the design task is done
from argus.geo import *

META = dict(name='Power panel', group='F', layer=0, sub='Electronics', step=11, color='frame', orient='zmin',
            note='Placeholder. Will hold the DC jack, KCD1 switch, inline fuse, LM2596 buck, 74HCT125 board and the Wago '
                 'connectors, with the jack and switch facing the back edge.',
            hw={'Wood screw 4x16': 4})


def build():
    plate = box(-130, -45, 100, 150, 0, 3)
    base = [(-125, 105), (-125, 145), (-50, 105), (-50, 145)]
    return cut(plate, *[wood_hole(x, y, 3, 0) for x, y in base]), [(x, y, 'Power panel') for x, y in base]
