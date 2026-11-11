# shared numbers for the x axis module, all from the spec
from argus.spec import P, pat

(Y_ROD_A, XZ), (Y_ROD_B, _) = pat('x_rods')      # rod centres (y, z)
SY, SZ = pat('x_screw')[0]                       # lead screw centre (y, z)
L, R = P['xblk_l'], P['xblk_r']                  # inner faces of the end blocks
EX, EY = P['x_endstop']                          # endstop sensor centre
ROD_X = (L - 10, R + 10)                         # rod ends
