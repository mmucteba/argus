# base plate and rubber feet (bought, no printed parts in this module)
from argus.geo import *
from argus.spec import P


def feet():
    bx0, bx1, by0, by1 = P['base']
    return [(bx0 + 18, by0 + 18), (bx1 - 18, by0 + 18), (bx0 + 18, by1 - 18), (bx1 - 18, by1 - 18)]


def add_bought(add):
    bx0, bx1, by0, by1 = P['base']
    bt = P['base_t']
    add('Base plate', box(bx0, bx1, by0, by1, -bt, 0), 'F', 0, 'mech', 'Base', 1, 'wood', density=0.6, buy='base',
        note='18 mm plywood (or 6 mm aluminium, then tap M4 instead of wood screws). The flat, heavy reference that every '
             'other part bolts to. Printing it is possible but it would be less flat and lighter, so buy it.',
        hw={'Wood screw 4x16': 4}, holes=[(x, y, 'foot (from below)') for x, y in feet()])
    for x, y in feet():
        add('Rubber foot', cyl(10, (x, y, -bt - 10), (x, y, -bt)), 'F', 0, 'mech', 'Base', 1, 'rubber', mass=5, buy='feet')
