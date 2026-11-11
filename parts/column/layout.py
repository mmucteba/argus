# shared numbers for the column and focus module, all from the spec
from argus.spec import P, pat

(ZX_A, ZY), (ZX, _) = pat('z_rods')              # rod centres (x, y); ZX is the +x rod
FZ0, FZ1, FZC = P['focus_z']                     # focus carriage bottom, top, bearing centre
GEAR_Z = 214.0                                   # gears sit between the top cap and the motor bracket
