# shared numbers for the y axis module, all from the spec
from argus.spec import P, pat

(YX_A, YZ), (YX_B, _) = pat('y_rods')            # rod centres (x, z)
YSX, YSZ = pat('y_screw')[0]                     # lead screw centre (x, z)
Z1 = P['xc_z'][1]                                # top of the x carriage, bottom of the y blocks
YT = YZ + 12                                     # top of the y blocks
C0, C1 = P['yc_z']                               # y carriage plate bottom, top
