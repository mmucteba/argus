# column: hollow tower with the lower z rod ear, everything optical hangs from it
from argus.geo import *
from argus.spec import P, pat
from parts.column.layout import ZY

META = dict(name='Column', group='F', layer=5, sub='Column and focus', step=8, color='frame', orient='zmin',
            note='Hollow 50 x 40 mm tower with the lower Z rod ear printed in. Prints standing, 200 mm tall; the 45 degree '
                 'roof and gusset avoid supports.',
            hw={'Wood screw 4x16': 4, 'M3 heat-set insert': 2})


def build():
    col = fuse(box(-25, 25, 92, 132, 0, 200), box(-35, 35, 84, 140, 0, 5),
               box(-30, 30, 66, 92, 110, 120), prism_yz([(66, 110), (92, 110), (92, 84)], -30, 30))
    roof = cq.Workplane('XY', origin=(0, 112, 186)).rect(42, 32).workplane(offset=14).rect(14, 4).loft().val()
    base = [(-30, 88), (30, 88), (-30, 136), (30, 136)]
    cuts = [box(-21, 21, 96, 128, 5, 186.01), roof]
    cuts += [cyl(P['rod_bore_d'] / 2, (x, y, 110), (x, y, 120.1)) for x, y in pat('z_rods')]
    cuts += [cyl(1.3, (10, 70, 109), (10, 70, 120.1))]   # spring hook hole
    cuts += [ins((x, y, 200), '-z', 6.0) for x, y in pat('column_to_cap')]
    cuts += [cyl(P['m3_clear_d'] / 2, (-26, y, z), (26, y, z)) for y, z in pat('column_to_overview')]
    cuts += [wood_hole(x, y, 5, 0) for x, y in base]
    return cut(col, *cuts), [(x, y, 'column') for x, y in base]
