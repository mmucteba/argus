# bought part geometry and their mounting cut-outs (catalog, owned by the integrator)
import math
from cadquery import Vector as V
from argus.geo import box, cyl, tube, fuse, hexprism


def lm8uu(c, axis):
    x, y, z = c
    h = 12.0
    p0, p1 = {'x': ((x - h, y, z), (x + h, y, z)), 'y': ((x, y - h, z), (x, y + h, z)),
              'z': ((x, y, z - h), (x, y, z + h))}[axis]
    return tube(7.5, 4.1, p0, p1)


def nema17(face, axis, sign, c1, c2):
    # face plane coordinate along axis, shaft points along sign, body on the other side
    s = 42.3 / 2
    if axis == 'x':
        b0, b1 = (face - 40, face) if sign > 0 else (face, face + 40)
        body = box(b0, b1, c1 - s, c1 + s, c2 - s, c2 + s)
        boss = cyl(11, (face, c1, c2), (face + 2 * sign, c1, c2))
        shaft = cyl(2.5, (face + 2 * sign, c1, c2), (face + 24 * sign, c1, c2))
    else:
        b0, b1 = (face - 40, face) if sign > 0 else (face, face + 40)
        body = box(c1 - s, c1 + s, b0, b1, c2 - s, c2 + s)
        boss = cyl(11, (c1, face, c2), (c1, face + 2 * sign, c2))
        shaft = cyl(2.5, (c1, face + 2 * sign, c2), (c1, face + 24 * sign, c2))
    return fuse(body, boss, shaft)


def nema_holes(axis, face, thick, c1, c2):
    out = []
    for a in (-15.5, 15.5):
        for b in (-15.5, 15.5):
            if axis == 'x':
                out.append(cyl(1.7, (face - 0.1, c1 + a, c2 + b), (face + thick + 0.1, c1 + a, c2 + b)))
            else:
                out.append(cyl(1.7, (c1 + a, face - 0.1, c2 + b), (c1 + a, face + thick + 0.1, c2 + b)))
    if axis == 'x':
        out.append(cyl(11.25, (face - 0.1, c1, c2), (face + thick + 0.1, c1, c2)))
    else:
        out.append(cyl(11.25, (c1, face - 0.1, c2), (c1, face + thick + 0.1, c2)))
    return out


def t8_nut(axis, flange_at, c1, c2, sign=1):
    # anti backlash nut, flange plane at flange_at, flange thickness 3.5 on +sign side, body through -sign side
    f0, f1 = flange_at, flange_at + 3.5 * sign
    if axis == 'x':
        fl = tube(11, 4.1, (f0, c1, c2), (f1, c1, c2))
        body = tube(5.1, 4.1, (f0, c1, c2), (f0 - 15 * sign, c1, c2))
        spring = tube(6.5, 4.1, (f1, c1, c2), (f1 + 9 * sign, c1, c2))
    else:
        fl = tube(11, 4.1, (c1, f0, c2), (c1, f1, c2))
        body = tube(5.1, 4.1, (c1, f0, c2), (c1, f0 - 15 * sign, c2))
        spring = tube(6.5, 4.1, (c1, f1, c2), (c1, f1 + 9 * sign, c2))
    return fuse(fl, body, spring)


def t8_mount_holes(axis, x_face_lo, x_face_hi, c1, c2):
    out = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        d1, d2 = 8 * math.cos(a), 8 * math.sin(a)
        if axis == 'x':
            out.append(cyl(1.9, (x_face_lo - 0.1, c1 + d1, c2 + d2), (x_face_hi + 0.1, c1 + d1, c2 + d2)))
            out.append(hexprism(5.7, 2.6, (x_face_lo - 0.01, c1 + d1, c2 + d2), 'x'))
        else:
            out.append(cyl(1.9, (c1 + d1, x_face_lo - 0.1, c2 + d2), (c1 + d1, x_face_hi + 0.1, c2 + d2)))
            out.append(hexprism(5.7, 2.6, (c1 + d1, x_face_lo - 0.01 + 2.6, c2 + d2), 'y').translate(V(0, -2.6, 0)))
    if axis == 'x':
        out.append(cyl(7.3, (x_face_lo - 0.1, c1, c2), (x_face_hi + 0.1, c1, c2)))
    else:
        out.append(cyl(7.3, (c1, x_face_lo - 0.1, c2), (c1, x_face_hi + 0.1, c2)))
    return out


def endstop_board(xc, yc, z, long_axis):
    # optical fork board, fork gap perpendicular to the long axis
    if long_axis == 'y':
        pcb = box(xc - 5.25, xc + 5.25, yc - 16.5, yc + 16.5, z, z + 1.6)
        base = box(xc - 3.15, xc + 3.15, yc - 12.25, yc + 12.25, z + 1.6, z + 4.4)
        p1 = box(xc - 3.15, xc + 3.15, yc + 1.55, yc + 12.25, z + 4.4, z + 12.4)
        p2 = box(xc - 3.15, xc + 3.15, yc - 12.25, yc - 1.55, z + 4.4, z + 12.4)
    else:
        pcb = box(xc - 16.5, xc + 16.5, yc - 5.25, yc + 5.25, z, z + 1.6)
        base = box(xc - 12.25, xc + 12.25, yc - 3.15, yc + 3.15, z + 1.6, z + 4.4)
        p1 = box(xc + 1.55, xc + 12.25, yc - 3.15, yc + 3.15, z + 4.4, z + 12.4)
        p2 = box(xc - 12.25, xc - 1.55, yc - 3.15, yc + 3.15, z + 4.4, z + 12.4)
    return fuse(pcb, base, p1, p2)
