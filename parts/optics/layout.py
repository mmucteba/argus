# shared numbers for the optics module, all from the spec
from argus.spec import P

LF = P['z_obj_tip']                              # lens front
ZC = P['z_cmount']                               # c mount flange
LR = P['lens_r']                                 # lens barrel radius
RING_Z = P['z_focal'] + P['ring_above_slide']    # led ring bottom
RING_TOP = RING_Z + 3.5
