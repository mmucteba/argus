# geometry helpers: every part is built from these
# units mm, z up; points are (x, y, z) tuples
import math
import cadquery as cq
from cadquery import Vector as V
from argus.spec import P

__all__ = ['math', 'cq', 'V', 'box', 'cyl', 'tube', 'cone', 'fuse', 'cut', 'orient_to', 'hexprism', 'prism_yz', 'ins', 'bolt_v', 'wood_hole', 'saddle', 'ziptie_slots', 'spur_gear']



def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return cq.Solid.makeCylinder(r, d.Length, p0, d.normalized())


def tube(ro, ri, p0, p1):
    return cyl(ro, p0, p1).cut(cyl(ri, p0, p1))


def cone(r0, r1, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return cq.Solid.makeCone(r0, r1, d.Length, p0, d.normalized())


def fuse(*s):
    out = s[0]
    for t in s[1:]:
        out = out.fuse(t)
    return out.clean()


def cut(a, *s):
    for t in s:
        a = a.cut(t)
    return a.clean()


def orient_to(solid, axis, p):
    # solid built along +z at origin, rotate to axis and move to p
    if axis == 'x':
        solid = solid.rotate(V(0, 0, 0), V(0, 1, 0), 90)
    elif axis == 'y':
        solid = solid.rotate(V(0, 0, 0), V(1, 0, 0), -90)
    return solid.translate(V(*p))


def hexprism(af, h, p, axis='z'):
    s = cq.Workplane('XY').polygon(6, af / math.cos(math.pi / 6)).extrude(h).val()
    return orient_to(s, axis, p)


def prism_yz(pts_yz, x0, x1):
    # polygon in the y z plane extruded along x from x0 to x1
    return cq.Workplane('YZ', origin=(x0, 0, 0)).polyline(pts_yz).close().extrude(x1 - x0).val()


def ins(p, axis='-z', depth=6.0):
    # m3 heat set insert hole, p is the opening on the surface, axis is drilling direction
    x, y, z = p
    d = {'-z': (0, 0, -1), '+z': (0, 0, 1), '-y': (0, -1, 0), '+y': (0, 1, 0), '-x': (-1, 0, 0), '+x': (1, 0, 0)}[axis]
    return cyl(P['insert_d'] / 2, p, (x + d[0] * depth, y + d[1] * depth, z + d[2] * depth))


def bolt_v(x, y, z_top, z_bot, cb_depth=0.0, r=None, cbr=3.1):
    # vertical m3 bolt hole with optional counterbore from the top
    r = r or P['m3_clear_d'] / 2
    s = cyl(r, (x, y, z_bot - 0.1), (x, y, z_top + 0.1))
    if cb_depth:
        s = s.fuse(cyl(cbr, (x, y, z_top - cb_depth), (x, y, z_top + 0.1)))
    return s


def wood_hole(x, y, z_top, z_bot, cb_to=None):
    # hole for a wood screw into the base plate, optional counterbore down to cb_to
    s = cyl(P['wood_screw_d'] / 2, (x, y, z_bot - 0.1), (x, y, z_top + 0.1))
    if cb_to is not None:
        s = s.fuse(cyl(4.3, (x, y, cb_to), (x, y, z_top + 0.1)))
    return s


def saddle(center, axis, length, half_w, open_dir, r=7.55, dip=1.0, wall=3.5, plate_face=None):
    # half pipe pocket for lm8uu that wraps the bearing past its centre by dip
    cx, cy, cz = center
    if axis == 'x' and open_dir == '-z':
        blk = box(cx - length / 2, cx + length / 2, cy - half_w, cy + half_w, cz - dip, plate_face)
        return blk, cyl(r, (cx - length / 2 - 1, cy, cz), (cx + length / 2 + 1, cy, cz))
    if axis == 'y' and open_dir == '-z':
        blk = box(cx - half_w, cx + half_w, cy - length / 2, cy + length / 2, cz - dip, plate_face)
        return blk, cyl(r, (cx, cy - length / 2 - 1, cz), (cx, cy + length / 2 + 1, cz))
    if axis == 'z' and open_dir == '+y':
        blk = box(cx - half_w, cx + half_w, plate_face, cy + dip, cz - length / 2, cz + length / 2)
        return blk, cyl(r, (cx, cy, cz - length / 2 - 1), (cx, cy, cz + length / 2 + 1))
    raise ValueError


def ziptie_slots(center, axis, open_dir, z0, z1, off=8.6, along=6.0):
    cx, cy, cz = center
    out = []
    for a in (-along, along):
        for s in (-1, 1):
            if axis == 'x':
                out.append(box(cx + a - 1.8, cx + a + 1.8, cy + s * off - 1.0, cy + s * off + 1.0, z0, z1))
            elif axis == 'y':
                out.append(box(cx + s * off - 1.0, cx + s * off + 1.0, cy + a - 1.8, cy + a + 1.8, z0, z1))
            else:
                out.append(box(cx + s * off - 1.0, cx + s * off + 1.0, z0, z1, cz + a - 1.8, cz + a + 1.8))
    return out


def spur_gear(m, z, t, bore=None, backlash=0.1, pa=20.0):
    r = m * z / 2
    rb = r * math.cos(math.radians(pa))
    ra = r + m
    rf = r - 1.25 * m
    inv = lambda a: math.tan(a) - a
    a_pitch = math.acos(rb / r)
    half_tooth = math.pi / (2 * z) - backlash / (2 * r)
    pts = []
    for k in range(z):
        c = 2 * math.pi * k / z
        prof = []
        for i in range(9):
            rr = rb + (ra - rb) * i / 8
            if rr < rb:
                rr = rb
            a = math.acos(min(1.0, rb / rr))
            th = half_tooth + inv(a_pitch) - inv(a)
            prof.append((rr, th))
        left = [(rr * math.cos(c - th), rr * math.sin(c - th)) for rr, th in prof]
        right = [(rr * math.cos(c + th), rr * math.sin(c + th)) for rr, th in reversed(prof)]
        th0 = prof[0][1]
        pts.append((rf * math.cos(c - th0 - 0.05), rf * math.sin(c - th0 - 0.05)))
        pts += left + right
        pts.append((rf * math.cos(c + th0 + 0.05), rf * math.sin(c + th0 + 0.05)))
    g = cq.Workplane('XY').polyline(pts).close().extrude(t).val()
    return g
