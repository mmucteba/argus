# bought part geometry and their mounting cut-outs (catalog, owned by the integrator)
import math
from cadquery import Vector as V
from argus.geo import box, cyl, tube, fuse, hexprism
from argus.spec import F, P


def lm8uu(c, axis):
    x, y, z = c
    h = F.lm8uu.length / 2
    p0, p1 = {'x': ((x - h, y, z), (x + h, y, z)), 'y': ((x, y - h, z), (x, y + h, z)),
              'z': ((x, y, z - h), (x, y, z + h))}[axis]
    return tube(F.lm8uu.od / 2, 4.1, p0, p1)


def nema17(face, axis, sign, c1, c2):
    # face plane coordinate along axis, shaft points along sign, body on the other side
    n = F.nema17
    s = n.body / 2
    bl, bh, sl = n.length, n.boss_h, n.boss_h + n.shaft_len
    if axis == 'x':
        b0, b1 = (face - bl, face) if sign > 0 else (face, face + bl)
        body = box(b0, b1, c1 - s, c1 + s, c2 - s, c2 + s)
        boss = cyl(n.boss_d / 2, (face, c1, c2), (face + bh * sign, c1, c2))
        shaft = cyl(n.shaft_d / 2, (face + bh * sign, c1, c2), (face + sl * sign, c1, c2))
    else:
        b0, b1 = (face - bl, face) if sign > 0 else (face, face + bl)
        body = box(c1 - s, c1 + s, b0, b1, c2 - s, c2 + s)
        boss = cyl(n.boss_d / 2, (c1, face, c2), (c1, face + bh * sign, c2))
        shaft = cyl(n.shaft_d / 2, (c1, face + bh * sign, c2), (c1, face + sl * sign, c2))
    return fuse(body, boss, shaft)


def nema_holes(axis, face, thick, c1, c2):
    out = []
    hs = F.nema17.hole_spacing / 2
    rc = P['m3_clear_d'] / 2
    rb = (F.nema17.boss_d + 0.5) / 2
    for a in (-hs, hs):
        for b in (-hs, hs):
            if axis == 'x':
                out.append(cyl(rc, (face - 0.1, c1 + a, c2 + b), (face + thick + 0.1, c1 + a, c2 + b)))
            else:
                out.append(cyl(rc, (c1 + a, face - 0.1, c2 + b), (c1 + a, face + thick + 0.1, c2 + b)))
    if axis == 'x':
        out.append(cyl(rb, (face - 0.1, c1, c2), (face + thick + 0.1, c1, c2)))
    else:
        out.append(cyl(rb, (c1, face - 0.1, c2), (c1, face + thick + 0.1, c2)))
    return out


def t8_nut(axis, flange_at, c1, c2, sign=1):
    # anti backlash nut, flange plane at flange_at, flange thickness 3.5 on +sign side, body through -sign side
    t = F.t8_nut
    rf, rb, rs, bl, sl = t.flange_d / 2, t.body_d / 2, t.spring_d / 2, t.body_len, t.spring_len
    f0, f1 = flange_at, flange_at + t.flange_t * sign
    if axis == 'x':
        fl = tube(rf, 4.1, (f0, c1, c2), (f1, c1, c2))
        body = tube(rb, 4.1, (f0, c1, c2), (f0 - bl * sign, c1, c2))
        spring = tube(rs, 4.1, (f1, c1, c2), (f1 + sl * sign, c1, c2))
    else:
        fl = tube(rf, 4.1, (c1, f0, c2), (c1, f1, c2))
        body = tube(rb, 4.1, (c1, f0, c2), (c1, f0 - bl * sign, c2))
        spring = tube(rs, 4.1, (c1, f1, c2), (c1, f1 + sl * sign, c2))
    return fuse(fl, body, spring)


def t8_mount_holes(axis, x_face_lo, x_face_hi, c1, c2):
    # nut holes 0.4 mm oversize so the nut can float into line, nut traps for m3 nuts
    out = []
    t, nut = F.t8_nut, F.m3_nut
    rh, rc = (t.hole_d + 0.4) / 2, t.spring_d / 2 + 0.8
    af, nh = nut.af + 0.2, nut.h + 0.2
    for k in range(4):
        a = math.radians(45 + 90 * k)
        d1, d2 = t.hole_circle / 2 * math.cos(a), t.hole_circle / 2 * math.sin(a)
        if axis == 'x':
            out.append(cyl(rh, (x_face_lo - 0.1, c1 + d1, c2 + d2), (x_face_hi + 0.1, c1 + d1, c2 + d2)))
            out.append(hexprism(af, nh, (x_face_lo - 0.01, c1 + d1, c2 + d2), 'x'))
        else:
            out.append(cyl(rh, (c1 + d1, x_face_lo - 0.1, c2 + d2), (c1 + d1, x_face_hi + 0.1, c2 + d2)))
            out.append(hexprism(af, nh, (c1 + d1, x_face_lo - 0.01 + nh, c2 + d2), 'y').translate(V(0, -nh, 0)))
    if axis == 'x':
        out.append(cyl(rc, (x_face_lo - 0.1, c1, c2), (x_face_hi + 0.1, c1, c2)))
    else:
        out.append(cyl(rc, (c1, x_face_lo - 0.1, c2), (c1, x_face_hi + 0.1, c2)))
    return out


def endstop_board(xc, yc, z, long_axis):
    # optical fork board, fork gap perpendicular to the long axis
    e = F.endstop_board
    pw, pl, fw, fl, g = e.pcb_w / 2, e.pcb_l / 2, e.fork_w / 2, e.fork_l / 2, e.gap / 2
    z1, z2, z3 = z + e.pcb_t, z + e.pcb_t + e.base_h, z + e.pcb_t + e.base_h + e.fork_h
    if long_axis == 'y':
        pcb = box(xc - pw, xc + pw, yc - pl, yc + pl, z, z1)
        base = box(xc - fw, xc + fw, yc - fl, yc + fl, z1, z2)
        p1 = box(xc - fw, xc + fw, yc + g, yc + fl, z2, z3)
        p2 = box(xc - fw, xc + fw, yc - fl, yc - g, z2, z3)
    else:
        pcb = box(xc - pl, xc + pl, yc - pw, yc + pw, z, z1)
        base = box(xc - fl, xc + fl, yc - fw, yc + fw, z1, z2)
        p1 = box(xc + g, xc + fl, yc - fw, yc + fw, z2, z3)
        p2 = box(xc - fl, xc - g, yc - fw, yc + fw, z2, z3)
    return fuse(pcb, base, p1, p2)
