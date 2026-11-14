# fit coupons: one flat plate with three sizes of every printed hole so the hole sizes in the spec can come from facts
import cadquery as cq
from argus.geo import *
from argus.spec import F

META = dict(name='Fit coupons', orient='zmin',
            note='Flat plate with rod bores, LM8UU saddles, 608 seats, insert, M3 clearance and M2.5 tap holes, '
                 'three sizes each with the size engraved next to it. Print flat with the parts settings, no supports, '
                 'then try the real rod, bearings, inserts and screws and report which size fits best.')

# plate
PX, PY, T = 100.0, 60.0, 10.0      # outline and thickness, the task allows 100 x 60 and 6 to 10 thick
ENGRAVE = 0.6                      # label depth
FONT = 3.5                         # label font size

# test sizes: nominal of the real part plus the steps from the task
ROD = [F.rod_8mm.d + s for s in (0.0, 0.1, 0.2)]
SADDLE = [F.lm8uu.od + s for s in (0.0, 0.1, 0.2)]
SEAT = [F.bearing_608.od + s for s in (0.0, 0.15, 0.3)]
INSERT = [F.m3_insert.hole_d + s for s in (-0.2, 0.0, 0.2)]
CLEAR = [3.2, 3.4, 3.6]            # m3 clearance tries
TAP = [2.0, 2.2, 2.4]              # m2.5 tap tries
INSERT_DEPTH = 6.0                 # blind insert hole depth as in the task


def label(d, x, y):
    # engraved size number centred on x y
    s = f'{d:.1f}' if abs(round(d, 1) - d) < 1e-6 else f'{d:.2f}'
    t = cq.Workplane('XY').text(s, FONT, ENGRAVE + 0.2, combine=False, halign='center', valign='center').val()
    return t.translate(cq.Vector(x, y, T - ENGRAVE))


def through(d, x, y):
    return cyl(d / 2, (x, y, -0.1), (x, y, T + 0.1))


def blind(d, depth, x, y):
    return cyl(d / 2, (x, y, T - depth), (x, y, T + 0.1))


def build():
    plate = box(0, PX, 0, PY, 0, T)
    cuts = []
    # 608 seats along the top left with labels under them
    for d, x in zip(SEAT, (13.0, 38.0, 63.0)):
        cuts += [blind(d, F.bearing_608.w, x, 46.5), label(d, x, 33.0)]
    # lm8uu saddles along y open on top with the axis on the top face and labels under them
    for d, x in zip(SADDLE, (9.5, 28.5, 47.5)):
        cuts += [cyl(d / 2, (x, 6.0, T), (x, 6.0 + F.lm8uu.length, T)), label(d, x, 3.0)]
    # rod bores and insert holes bottom right
    for i, x in enumerate((64.0, 78.0, 92.0)):
        cuts += [through(ROD[i], x, 23.0), label(ROD[i], x, 15.0)]
        cuts += [blind(INSERT[i], INSERT_DEPTH, x, 8.5), label(INSERT[i], x, 2.5)]
    # m3 clearance and m2.5 tap holes top right
    for i, x in enumerate((81.0, 88.5, 96.0)):
        cuts += [through(CLEAR[i], x, 54.0), label(CLEAR[i], x, 48.5)]
        cuts += [through(TAP[i], x, 42.5), label(TAP[i], x, 37.0)]
    return cut(plate, *cuts)
