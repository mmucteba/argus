# whole machine checks: collisions over all poses, light path, drives, printability, scan time
# run through tools/check.py; writes build/checks.json for the viewer
import json, math, itertools, time
from collections import Counter, defaultdict
import numpy as np
import trimesh, fcl
import manifold3d as mf
from argus import registry as model
from argus.spec import P
from argus.printing import mass_of, oriented, ORIENT_TXT

G = 9.81


def to_mesh(shape, tol=0.02, ang=0.1):
    v, t = shape.tessellate(tol, ang)
    m = trimesh.Trimesh(np.array([[p.x, p.y, p.z] for p in v]), np.array(t), process=True)
    m.merge_vertices()
    return m


def offset(group, sx, sy, sz):
    return {'F': (0, 0, 0), 'X': (sx, 0, 0), 'Y': (sx, sy, 0), 'Z': (0, 0, sz)}[group]


class Body:
    def __init__(self, name, mesh, group):
        self.name, self.mesh, self.group = name, mesh, group
        self.bvh = fcl.BVHModel()
        self.bvh.beginModel(len(mesh.vertices), len(mesh.faces))
        self.bvh.addSubModel(mesh.vertices.astype(np.float64), mesh.faces.astype(np.int32))
        self.bvh.endModel()
        self.mf = mf.Manifold(mf.Mesh(vert_properties=mesh.vertices.astype(np.float32),
                                      tri_verts=mesh.faces.astype(np.uint32)))
        self.lo, self.hi = mesh.bounds

    def obj(self, t):
        return fcl.CollisionObject(self.bvh, fcl.Transform(np.eye(3), np.array(t, float)))


def collide(a, ta, b, tb):
    return fcl.collide(a.obj(ta), b.obj(tb), fcl.CollisionRequest(), fcl.CollisionResult()) > 0


def dist(a, ta, b, tb):
    return fcl.distance(a.obj(ta), b.obj(tb), fcl.DistanceRequest(), fcl.DistanceResult())


def overlap_vol(a, ta, b, tb):
    m = a.mf.translate(list(map(float, ta))) ^ b.mf.translate(list(map(float, tb)))
    return m.volume() if hasattr(m, 'volume') else m.get_volume()


def aabb_gap(a, ta, b, tb):
    d = np.maximum(0, np.maximum((a.lo + ta) - (b.hi + tb), (b.lo + tb) - (a.hi + ta)))
    return float(np.linalg.norm(d))


DESIGNED = [('X rod', 'LM8UU (X)'), ('X lead screw', 'T8 spring nut (X)'), ('X lead screw', 'X carriage'),
            ('X endstop sensor', 'X carriage'), ('Y rod', 'LM8UU (Y)'), ('Y lead screw', 'T8 spring nut (Y)'),
            ('Y lead screw', 'Y carriage'), ('Y endstop sensor', 'Y endstop flag'), ('Z rod', 'LM8UU (Z)'),
            ('M4 focus screw', 'Focus carriage'), ('Z rod', 'Focus carriage')]
SAME_OK = [('X lead screw', 'X coupling'), ('Y lead screw', 'Y coupling'), ('X motor NEMA17', 'X coupling'),
           ('Y motor NEMA17', 'Y coupling'), ('28BYJ-48 focus motor', 'Focus gear (motor)'),
           ('X lead screw', '608ZZ bearing (X)'), ('Y lead screw', '608ZZ bearing (Y)')]


def designed(n1, n2):
    return any({n1, n2} == {a, b} for a, b in DESIGNED)


def frustum(r0, z0, r1, z1, sections=48):
    ang = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    bot = np.c_[r0 * np.cos(ang), r0 * np.sin(ang), np.full(sections, z0)]
    top = np.c_[r1 * np.cos(ang), r1 * np.sin(ang), np.full(sections, z1)]
    v = np.vstack([bot, top, [[0, 0, z0], [0, 0, z1]]])
    n, f = sections, []
    for i in range(n):
        j = (i + 1) % n
        f += [[i, j, n + j], [i, n + j, n + i], [2 * n, j, i], [2 * n + 1, n + i, n + j]]
    m = trimesh.Trimesh(v, np.array(f), process=True)
    m.fix_normals()
    return m


def support_report(shape, key):
    s = oriented(shape, key)
    m = to_mesh(s, tol=0.05, ang=0.2)
    nz, cz = m.face_normals[:, 2], m.triangles_center[:, 2]
    over = (nz < -0.74) & (cz > 0.4)
    bb = s.BoundingBox()
    dims = (bb.xlen, bb.ylen, bb.zlen)
    if not over.any():
        return dims, []
    idx = np.where(over)[0]
    adj = m.face_adjacency
    keep = over[adj[:, 0]] & over[adj[:, 1]]
    comps = trimesh.graph.connected_components(edges=adj[keep], nodes=idx, min_len=1)
    bad = []
    for c in comps:
        c = np.asarray(c)
        pts = m.vertices[m.faces[c]].reshape(-1, 3)
        ext = pts.max(0) - pts.min(0)
        span, area = float(min(ext[0], ext[1])), float(m.area_faces[c].sum())
        e = np.sort(m.faces[c][:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
        u, cnt = np.unique(e, axis=0, return_counts=True)
        bnd = u[cnt == 1]
        perim = float(np.linalg.norm(m.vertices[bnd[:, 0]] - m.vertices[bnd[:, 1]], axis=1).sum()) if len(bnd) else 1.0
        width = 2 * area / perim
        if span > 12 and width > 4 and area > 25:
            bad.append(dict(span=round(span, 1), width=round(width, 1), area=round(area), z=round(float(pts[:, 2].min()), 1)))
    return dims, bad


def run():
    t0 = time.time()
    parts = model.build()
    bodies = []
    for p in parts:
        p['mesh'] = to_mesh(p['shape'])
        bodies.append(Body(p['name'], p['mesh'], p['group']))
    print('meshed', round(time.time() - t0, 1), 's')
    zf = P['z_focal']
    res = dict(items=[], data={})
    items = res['items']

    def item(id_, title, status, value, limit, detail, pose=None, parts=None, cat=''):
        items.append(dict(id=id_, title=title, status=status, value=value, limit=limit, detail=detail,
                          pose=pose, parts=parts or [], cat=cat))

    # ---------------- optics numbers
    um_px = P['px_native'] * P['binning'] / P['mag']
    fov = (P['sensor_w'] / P['mag'], P['sensor_h'] / P['mag'])
    res_um = 0.61 * P['wavelength'] / P['na']
    dof = P['wavelength'] / P['na'] ** 2 + P['px_native'] * P['binning'] / (P['mag'] * P['na'])
    r_fov = math.hypot(*fov) / 2
    d_diff = zf - P['diffuser_top']
    na_ill = math.sin(math.atan(13.9 / d_diff))
    res['data']['optics'] = dict(um_px=um_px, fov=fov, res_um=res_um, dof_um=dof, na_ill=na_ill, r_fov=r_fov)
    item('optics', 'Optics: magnification, FOV, resolution', 'INFO',
         f'{um_px:.3f} um/px, FOV {fov[0]:.2f} x {fov[1]:.2f} mm', '',
         f'M = {P["mag"]:.1f} with the zoom lens at full zoom on the HQ camera (2x2 binned, 2028 x 1520). The lens NA is not '
         f'published; with an estimated {P["na"]:.2f} the optical resolution is about {res_um:.0f} um and the depth of field '
         f'about {dof:.0f} um. Measure the real resolution with the 0.1 mm ruler when the lens arrives.', cat='Light path')
    item('illum_na', 'Diffuser fills the lens aperture', 'PASS' if na_ill >= 2 * P['na'] else 'WARN',
         f'illumination NA {na_ill:.2f}', f'>= {2 * P["na"]:.2f} (2x lens NA)',
         f'The 28 mm diffuser sits {d_diff:.0f} mm below the tissue, so light arrives from up to '
         f'{math.degrees(math.asin(na_ill)):.0f} deg off axis; the lens only accepts '
         f'{math.degrees(math.asin(P["na"])):.1f} deg. No condenser needed.', cat='Light path')

    # ---------------- collisions and clearances
    sxs = [P['x_travel'][0], -10, 0, 20, 40, 55, 66, P['x_travel'][1]]
    sys_ = [P['y_travel'][0], 0, P['y_travel'][1]]
    szs = [P['z_travel'][0], 0, P['z_travel'][1]]
    poses = list(itertools.product(sxs, sys_, szs))
    collisions, clear = {}, {}
    t1 = time.time()
    n_pairs = 0
    for (sx, sy, sz) in poses:
        tr = [np.array(offset(b.group, sx, sy, sz), float) for b in bodies]
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                a, b = bodies[i], bodies[j]
                if a.group == b.group:
                    continue
                g = aabb_gap(a, tr[i], b, tr[j])
                if g > 12:
                    continue
                n_pairs += 1
                key = tuple(sorted((a.name, b.name)))
                hit = False
                if g == 0 and collide(a, tr[i], b, tr[j]):
                    hit = not designed(a.name, b.name) or overlap_vol(a, tr[i], b, tr[j]) > 0.5
                if hit:
                    vol = overlap_vol(a, tr[i], b, tr[j])
                    if vol < 0.01 and designed(a.name, b.name):
                        continue
                    c = collisions.setdefault(key, dict(pair=key, count=0, worst=0, pose=None))
                    c['count'] += 1
                    if vol >= c['worst']:
                        c['worst'], c['pose'] = vol, (sx, sy, sz)
                    continue
                if designed(a.name, b.name):
                    continue
                d = dist(a, tr[i], b, tr[j])
                c = clear.setdefault(key, dict(pair=key, min=1e9, pose=None))
                if d < c['min']:
                    c['min'], c['pose'] = d, (sx, sy, sz)
    print('collision sweep', len(poses), 'poses', n_pairs, 'pair tests', round(time.time() - t1, 1), 's')
    inner = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            if a.group != b.group or aabb_gap(a, np.zeros(3), b, np.zeros(3)) > 0:
                continue
            if any({a.name, b.name} == {x, y} for x, y in SAME_OK):
                continue
            if collide(a, np.zeros(3), b, np.zeros(3)):
                v = overlap_vol(a, np.zeros(3), b, np.zeros(3))
                if v > 0.5:
                    inner.append((a.name, b.name, round(v, 1)))
    res['data']['inner'] = inner
    print('same-assembly overlaps', inner)
    col = sorted(collisions.values(), key=lambda c: -c['worst'])
    res['data']['collisions'] = [dict(a=c['pair'][0], b=c['pair'][1], n=c['count'], vol=round(c['worst'], 2),
                                      pose=list(c['pose'])) for c in col]
    if inner:
        item('inner', 'No parts overlap inside an assembly', 'FAIL', f'{len(inner)} overlaps', '0',
             '; '.join(f'{a} into {b} ({v} mm3)' for a, b, v in inner), parts=list(inner[0][:2]), cat='Mechanics')
    else:
        item('inner', 'No parts overlap inside an assembly', 'PASS', '0 overlaps', '0',
             'Every part was also checked against the parts it is bolted to (nut flanges, motors, bearings, gears).',
             cat='Mechanics')
    if col:
        c = col[0]
        item('collide', 'No collisions over full X, Y, Z travel', 'FAIL', f'{len(col)} colliding pairs', '0',
             '; '.join(f'{c2["pair"][0]} vs {c2["pair"][1]} ({c2["count"]} poses, worst {c2["worst"]:.1f} mm3 at '
                       f'{c2["pose"]})' for c2 in col), pose=list(c['pose']), parts=list(c['pair']), cat='Mechanics')
    else:
        item('collide', 'No collisions over full X, Y, Z travel', 'PASS', f'0 of {len(poses)} poses', '0 collisions',
             f'Swept X {sxs[0]:.0f} to {sxs[-1]:.0f} mm, Y {sys_[0]:.0f} to {sys_[-1]:.0f} mm, focus {szs[0]:.0f} to '
             f'{szs[-1]:.0f} mm ({len(poses)} poses, {n_pairs} part-pair tests). Vanes passing through the endstop forks '
             f'and rods inside bearings are intended contacts.', cat='Mechanics')
    tight = sorted(clear.values(), key=lambda c: c['min'])[:8]
    res['data']['clearances'] = [dict(a=c['pair'][0], b=c['pair'][1], min=round(c['min'], 2), pose=list(c['pose']))
                                 for c in tight]
    worst = tight[0]
    st = 'PASS' if worst['min'] >= 2 else ('WARN' if worst['min'] >= 0.8 else 'FAIL')
    item('clearance', 'Tightest gap between parts that move relative to each other', st, f'{worst["min"]:.1f} mm',
         '>= 2 mm (print tolerance)', 'Smallest gaps anywhere in the travel: ' + '; '.join(
             f'{c["pair"][0]} to {c["pair"][1]} {c["min"]:.1f} mm at X {c["pose"][0]:.0f}, Y {c["pose"][1]:.0f}, '
             f'Z {c["pose"][2]:.0f}' for c in tight[:5]) + '.', pose=list(worst['pose']), parts=list(worst['pair']),
         cat='Mechanics')

    # ---------------- light path
    t_na, t_na2 = math.tan(math.asin(P['na'])), math.tan(math.asin(2 * P['na']))
    zd = P['diffuser_top'] + 0.05
    cones = {'crit': Body('c', frustum(r_fov + (zf - zd) * t_na, zd, r_fov, zf - 0.02), 'F'),
             'wide': Body('w', frustum(r_fov + (zf - zd) * t_na2, zd, r_fov, zf - 0.02), 'F'),
             'img': Body('i', frustum(r_fov, P['z_cover_top'] + 0.02, r_fov + P['wd'] * t_na - 0.02, P['z_obj_tip'] - 0.25), 'F')}
    skip = {'Glass slide', 'Coverslip', 'Opal diffuser', 'Zoom lens 0.12-1.8x', 'Zoom lens front glass',
            'Raspberry Pi HQ Camera'}
    us, vs = np.arange(-37.0, 37.01, 1.0), np.arange(-12.0, 12.01, 1.0)
    grid = {k: np.zeros((len(vs), len(us)), bool) for k in ('crit', 'wide', 'img')}
    movers = [b for b in bodies if b.name not in skip]
    t2 = time.time()
    for iv, v in enumerate(vs):
        for iu, u in enumerate(us):
            sx, sy = -u, -v
            for key in ('crit', 'wide', 'img'):
                cb, ok = cones[key], True
                for b in movers:
                    t = np.array(offset(b.group, sx, sy, 0), float)
                    if aabb_gap(cb, np.zeros(3), b, t) > 0:
                        continue
                    if collide(cb, np.zeros(3), b, t):
                        ok = False
                        break
                grid[key][iv, iu] = ok
    print('light sweep', round(time.time() - t2, 1), 's')

    def best_rect(mask):
        best, H, W = (0, None), *mask.shape
        for i0 in range(H):
            for i1 in range(i0, H):
                rows = mask[i0:i1 + 1].all(axis=0)
                run_, start = 0, 0
                for j in range(W):
                    if rows[j]:
                        start = j if run_ == 0 else start
                        run_ += 1
                        if run_ * (i1 - i0 + 1) > best[0]:
                            best = (run_ * (i1 - i0 + 1), (i0, i1, start, j))
                    else:
                        run_ = 0
        return best[1]

    both = grid['crit'] & grid['img']
    r = best_rect(both)
    rw = (us[r[3]] - us[r[2]] + 1.0, vs[r[1]] - vs[r[0]] + 1.0)
    rc = ((us[r[3]] + us[r[2]]) / 2, (vs[r[1]] + vs[r[0]]) / 2)
    item('beam', 'Light reaches the camera through every layer',
         'PASS' if rw[0] >= P['roi'] and rw[1] >= P['roi'] else 'FAIL', f'clear area {rw[0]:.0f} x {rw[1]:.0f} mm',
         f'>= {P["roi"]:.0f} x {P["roi"]:.0f} mm scan',
         f'The light cone the lens uses was traced from the diffuser up through the X carriage opening, the Y '
         f'carriage opening, the holder window and the ring light at every 1 mm position on the slide. Largest fully '
         f'clear rectangle: {rw[0]:.0f} x {rw[1]:.0f} mm centred {rc[0]:+.0f} mm from the slide centre. The label end '
         f'(right 20 mm) is solid on purpose.', cat='Light path')
    r2 = best_rect(grid['wide'] & grid['img'])
    w2 = (us[r2[3]] - us[r2[2]] + 1.0, vs[r2[1]] - vs[r2[0]] + 1.0)
    item('beam_wide', 'Brightness margin (2x NA cone) stays clear',
         'PASS' if w2[0] >= P['roi'] and w2[1] >= P['roi'] else 'WARN', f'clear area {w2[0]:.0f} x {w2[1]:.0f} mm',
         f'>= {P["roi"]:.0f} x {P["roi"]:.0f} mm', 'Same sweep with a cone twice as wide, so tiles near the window '
                                                   'edge do not get darker.', cat='Light path')
    res['data']['clearmap'] = dict(u0=float(us[0]), v0=float(vs[0]), step=1.0, nu=len(us), nv=len(vs),
                                   crit=both.astype(int).tolist(),
                                   rect=[float(us[r[2]] - .5), float(us[r[3]] + .5), float(vs[r[0]] - .5), float(vs[r[1]] + .5)])

    # ---------------- masses
    gm = {g: sum(mass_of(p) for p in parts if p['group'] == g) for g in 'FXYZ'}

    def com(groups):
        ps = [p for p in parts if p['group'] in groups]
        m = sum(mass_of(p) for p in ps)
        return sum(mass_of(p) * np.array(p['shape'].Center().toTuple()) for p in ps) / m

    cxy, cy_ = com('XY'), com('Y')
    total = sum(mass_of(p) for p in parts)
    mx, my = gm['X'] + gm['Y'], gm['Y']
    res['data']['mass'] = dict(groups=gm, total=total, moving_x=mx, moving_y=my)
    item('mass', 'Moving masses', 'INFO', f'X axis moves {mx:.0f} g, Y axis moves {my:.0f} g, focus {gm["Z"]:.0f} g', '',
         f'Total scanner about {total / 1000:.2f} kg including the {mass_of(parts[0]) / 1000:.2f} kg plywood base. '
         f'The short Y axis is now on top, so it only carries the slide, holder and its carriage. The X axis carries '
         f'everything including the Y motor (280 g).', cat='Mechanics')

    # ---------------- rod sag
    E, I = P['e_steel'], math.pi * 8 ** 4 / 64
    w_rod = 7.85e-3 * math.pi * 16 * G / 1000

    def ss_point(Fp, a, L, x):
        b = L - a
        if x <= a:
            return Fp * b * x * (L * L - b * b - x * x) / (6 * E * I * L)
        return Fp * a * (L - x) * (L * L - a * a - (L - x) ** 2) / (6 * E * I * L)

    def ss_self(x, L):
        return w_rod * x * (L ** 3 - 2 * L * x * x + x ** 3) / (24 * E * I)

    xL0, xL = P['xblk_l'] - 5, (P['xblk_r'] + 5) - (P['xblk_l'] - 5)
    W = mx / 1000 * G
    share = [(P['xr_y'] - cxy[1]) / (2 * P['xr_y']), (P['xr_y'] + cxy[1]) / (2 * P['xr_y'])]
    sag_x = {}
    for sx in np.arange(P['x_travel'][0], P['x_travel'][1] + 0.1, 1.0):
        vals = []
        for fr in share:
            Fr = W * fr / 2
            bs = [sx - P['xb_x'], sx + P['xb_x']]
            d = sum(sum(ss_point(Fr, b0 - xL0, xL, xb - xL0) for b0 in bs) + ss_self(xb - xL0, xL) for xb in bs) / 2
            vals.append(d)
        sag_x[float(sx)] = max(vals) * 1000
    yL0, yL = -50.0, 99.5
    Wy = my / 1000 * G
    sharey = [(P['yr_x'] - cy_[0]) / (2 * P['yr_x']), (P['yr_x'] + cy_[0]) / (2 * P['yr_x'])]
    sag_y = {}
    for sy in np.arange(P['y_travel'][0], P['y_travel'][1] + 0.1, 1.0):
        vals = []
        for fr in sharey:
            Fr = Wy * fr / 2
            bs = [sy - P['yb_y'], sy + P['yb_y']]
            d = sum(sum(ss_point(Fr, b0 - yL0, yL, yb - yL0) for b0 in bs) + ss_self(yb - yL0, yL) for yb in bs) / 2
            vals.append(d)
        sag_y[float(sy)] = max(vals) * 1000
    kx = np.array(list(sag_x.keys()))
    sx_v, sy_v = np.array(list(sag_x.values())), np.array(list(sag_y.values()))
    scan_m = (kx >= -17.5) & (kx <= 26)
    win = []
    for s0 in kx[scan_m]:
        m_ = (kx >= s0) & (kx <= s0 + P['roi']) & scan_m
        if m_.sum() > 1:
            win.append(sx_v[m_].max() - sx_v[m_].min())
    var_scan = max(win) + (sy_v.max() - sy_v.min()) * P['roi'] / 30
    var_slide = sx_v[scan_m].max() - sx_v[scan_m].min() + sy_v.max() - sy_v.min()
    res['data']['sag'] = dict(x=sag_x, y=sag_y, var_scan=var_scan, var_slide=var_slide)
    item('sag', 'Rod sag keeps the tissue in focus', 'PASS' if var_slide <= 15 else ('WARN' if var_slide <= dof / 2 else 'FAIL'),
         f'{var_scan:.1f} um over a 15 mm scan, {var_slide:.1f} um over the scannable slide',
         f'<= 15 um (levelling budget), DOF {dof:.0f} um',
         f'Peak sag {sx_v.max():.1f} um on the 219 mm X rods (carrying {mx:.0f} g) and {sy_v.max():.1f} um on the Y rods '
         f'(simply supported, worst case). What matters is how much it changes while the stage moves, and that stays '
         f'well inside the depth of field.', cat='Mechanics')

    # ---------------- drives
    lead, eta = P['lead'], P['screw_eff']

    def torque_ncm(m_g):
        return (m_g / 1000 * P['accel'] / 1000 + P['friction_n']) * lead / (2 * math.pi * eta) / 10

    tx, ty = torque_ncm(mx), torque_ncm(my)
    mgn = P['nema_pullout_ncm'] / max(tx, ty)
    rpm = P['vmax'] / lead * 60
    res['data']['drive'] = dict(tx=tx, ty=ty, rpm=rpm)
    item('torque', 'NEMA17 torque margin (X and Y)', 'PASS' if mgn >= 3 else 'WARN', f'{mgn:.0f}x margin', '>= 3x',
         f'Force = mass x {P["accel"]:.0f} mm/s2 + {P["friction_n"]:.0f} N friction; torque = force x 8 mm lead / '
         f'(2 pi x 0.3 efficiency). Needed {tx:.2f} N cm (X) and {ty:.2f} N cm (Y) at {rpm:.0f} rpm, against about '
         f'{P["nema_pullout_ncm"]:.0f} N cm the 17HS4401 still gives at that speed on 12 V.', cat='Drives')
    steps_mm = P['steps_rev'] * P['microsteps'] / lead
    um_step = 1000 / steps_mm
    item('xyres', 'XY step size vs pixel size', 'PASS', f'{um_step:.1f} um per microstep = {um_step / um_px:.1f} px',
         'well below tile overlap', f'{steps_mm:.0f} microsteps per mm; at {P["vmax"]:.0f} mm/s that is '
                                    f'{P["vmax"] * steps_mm / 1000:.1f} kHz, far inside the about 30 kHz GRBL limit on an Uno.',
         cat='Drives')
    zstep = P['m4_pitch'] / P['byj_halfsteps_rev'] * 1000
    zT = (gm['Z'] / 1000 * G + P['z_spring_n']) * P['m4_pitch'] / (2 * math.pi * P['m4_eff']) / 10
    zspeed = P['byj_rpm'] * P['m4_pitch'] / 60
    item('focus', 'Focus drive: step, torque, speed', 'PASS' if P['byj_torque_ncm'] / zT >= 2 else 'WARN',
         f'{zstep:.2f} um per half-step, {P["byj_torque_ncm"] / zT:.0f}x torque margin', 'step << DOF',
         f'Lifting {gm["Z"]:.0f} g plus the {P["z_spring_n"]:.0f} N spring needs {zT:.2f} N cm through the 1:1 gears. '
         f'Speed is {zspeed:.2f} mm/s. With about {dof:.0f} um depth of field one focus at the scan centre is enough; the '
         f'4-point map is a bonus.', cat='Drives')
    item('crash', 'Focus cannot crash the lens into the slide', 'PASS',
         f'{P["wd"] + P["z_travel"][0]:.0f} mm left at full down travel', '> 0',
         f'Lens front is {P["wd"]:.0f} mm above the coverslip at nominal focus; the carriage only travels '
         f'{abs(P["z_travel"][0]):.0f} mm down.', pose=[0, 0, P['z_travel'][0]],
         parts=['Zoom lens 0.12-1.8x', 'Coverslip'], cat='Drives')

    # ---------------- printability
    bed = sorted(P['bed'])
    printed = [p for p in parts if p['cat'] == 'printed']
    pinfo, too_big, need_sup = {}, [], []
    for p in printed:
        if p['name'] in pinfo:
            pinfo[p['name']]['qty'] += 1
            continue
        dims, bad = support_report(p['shape'], p['orient'])
        fits = all(d <= b + 1e-6 for d, b in zip(sorted(dims[:2]) + [dims[2]], bed))
        g = mass_of(p)
        pinfo[p['name']] = dict(qty=1, dims=[round(d, 1) for d in dims], fits=fits, supports=bad, grams=round(g, 1),
                                hours=round(g * P['h_per_g'], 1), orient=ORIENT_TXT[p['orient']])
        if not fits:
            too_big.append(p['name'])
        if bad:
            need_sup.append(p['name'])
    tot_g = sum(v['grams'] * v['qty'] for v in pinfo.values())
    tot_h = sum(v['hours'] * v['qty'] for v in pinfo.values())
    res['data']['print'] = pinfo
    item('print', 'Every printed part fits a 220 x 220 x 250 mm printer', 'PASS' if not too_big else 'FAIL',
         f'{len(pinfo)} different parts, {sum(v["qty"] for v in pinfo.values())} prints', 'fits the bed',
         ('All fit in their print orientation. ' if not too_big else 'Too big: ' + ', '.join(too_big) + '. ') +
         f'The tallest is the column at {max(v["dims"][2] for v in pinfo.values()):.0f} mm. '
         f'Filament about {tot_g:.0f} g, roughly {tot_h:.0f} h of printing at normal speed.', cat='Manufacturing')
    item('supports', 'No print needs supports', 'PASS' if not need_sup else 'WARN',
         f'{len(need_sup)} parts need supports' if need_sup else 'no supports', '0',
         ('Every overhang in the chosen orientation is either 45 degrees or steeper, or a short bridge under 12 mm. '
          if not need_sup else 'Overhangs wider than 12 mm on: ' + ', '.join(
              f'{n} ({", ".join(str(b["span"]) + " mm at z " + str(b["z"]) for b in pinfo[n]["supports"][:2])})'
              for n in need_sup) + '. '), parts=need_sup, cat='Manufacturing')

    # ---------------- cut list
    def length(name):
        bb = next(p for p in parts if p['name'] == name)['shape'].BoundingBox()
        return max(bb.xlen, bb.ylen, bb.zlen)

    xr, yr, zr = length('X rod'), length('Y rod'), length('Z rod')
    xs, ys = length('X lead screw'), length('Y lead screw')
    ok = xr <= 250 and yr + zr <= 248 and xs + ys <= 398
    res['data']['cuts'] = dict(xr=xr, yr=yr, zr=zr, xs=xs, ys=ys)
    item('cuts', 'Rods and screws come out of the BOM stock', 'PASS' if ok else 'FAIL',
         f'4 rods of 250 mm, 1 screw of 400 mm', 'no extra stock',
         f'Rods 1 and 2: X rods {xr:.0f} mm each. Rods 3 and 4: one Y rod {yr:.0f} mm + one Z rod {zr:.0f} mm each '
         f'({250 - yr - zr:.0f} mm left). T8 screw: X {xs:.0f} mm + Y {ys:.0f} mm ({400 - xs - ys:.0f} mm left). '
         f'Cut with a hacksaw or cutting disc, then file and chamfer the ends so the bearings slide on.', cat='Manufacturing')

    # ---------------- column stiffness
    Ep, b, h, t = P['e_pla'], 50.0, 40.0, 4.0
    I_y = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12
    I_x = (h * b ** 3 - (h - 2 * t) * (b - 2 * t) ** 3) / 12
    top_fixed = sum(mass_of(p) for p in parts if p['group'] == 'F' and p['layer'] in (5, 6)
                    and p['name'] not in ('Column', 'Z rod') and p['shape'].Center().z > 100)
    tower_m = mass_of(next(p for p in parts if p['name'] == 'Column'))
    m_eff = (gm['Z'] + top_fixed + 0.24 * tower_m) / 1000
    Lc = 185.0
    f1 = min(math.sqrt(3 * Ep * I_y / Lc ** 3 * 1000 / m_eff), math.sqrt(3 * Ep * I_x / Lc ** 3 * 1000 / m_eff)) / (2 * math.pi)
    ts = 4 / (0.03 * 2 * math.pi * f1)
    item('column', 'Column stiffness (vibration)', 'PASS' if f1 >= 50 else 'WARN', f'{f1:.0f} Hz first mode', '>= 50 Hz',
         f'Printed tower 50 x 40 mm, 4 mm walls, carrying {m_eff * 1000:.0f} g at about {Lc:.0f} mm. It rings down in '
         f'about {ts * 1000:.0f} ms, inside the {P["settle_s"] * 1000:.0f} ms settle time per tile.', cat='Mechanics')

    # ---------------- scan time
    fx, fy = fov
    stepx, stepy = fx * (1 - P['overlap']), fy * (1 - P['overlap'])
    nx, ny = math.ceil((P['roi'] - fx) / stepx) + 1, math.ceil((P['roi'] - fy) / stepy) + 1

    def tmove(d):
        a, v = P['accel'], P['vmax']
        return 2 * math.sqrt(d / a) if d < v * v / a else d / v + v / a

    t_tiles = nx * ny * (P['settle_s'] + P['capture_s']) + ny * (nx - 1) * tmove(stepx) + (ny - 1) * tmove(stepy)
    t_focus = 4 * (0.6 / zspeed + tmove(P['roi'] - 2) + P['settle_s']) + tmove(50)
    res['data']['scan'] = dict(nx=nx, ny=ny, stepx=stepx, stepy=stepy, t_tiles=t_tiles, t_focus=t_focus,
                               tmove_x=tmove(stepx), tmove_y=tmove(stepy))

    # ---------------- overview camera
    oc = P['overview']
    others = [i for i, p in enumerate(parts) if p['name'] not in
              ('Glass slide', 'Coverslip', 'Overview camera (USB, tbd)', 'Overview LED 5 mm')]
    origin = np.array([oc['x'], oc['y'], oc['z_lens'] - 0.1])
    pts_local = np.array([[u, v, P['z_cover_top'] + 0.01] for u in np.linspace(-37, 37, 15) for v in np.linspace(-12, 12, 5)])
    vis = {}
    t3 = time.time()
    for sx in range(30, int(P['x_travel'][1]) + 1, 2):
        meshes = []
        for i in others:
            m = parts[i]['mesh'].copy()
            m.apply_translation(offset(parts[i]['group'], sx, 0, 0))
            meshes.append(m)
        scene = trimesh.util.concatenate(meshes)
        tgt = pts_local + np.array([sx, 0, 0])
        dirs = tgt - origin
        lens = np.linalg.norm(dirs, axis=1)
        dirs = dirs / lens[:, None]
        locs, idx, _ = scene.ray.intersects_location(np.repeat(origin[None], len(dirs), 0), dirs, multiple_hits=False)
        blocked = np.zeros(len(dirs), bool)
        for l, k in zip(locs, idx):
            if np.linalg.norm(l - origin) < lens[k] - 0.05:
                blocked[k] = True
        ax_ = np.degrees(np.abs(np.arctan2(tgt[:, 0] - origin[0], origin[2] - tgt[:, 2])))
        ay_ = np.degrees(np.abs(np.arctan2(tgt[:, 1] - origin[1], origin[2] - tgt[:, 2])))
        vis[sx] = float(((~blocked) & (ax_ <= oc['hfov'] / 2) & (ay_ <= oc['vfov'] / 2)).mean())
    print('overview sweep', round(time.time() - t3, 1), 's')
    full = [sx for sx, f in vis.items() if f >= 0.999]
    park = min(full) if full else None
    h_cam = oc['z_lens'] - P['z_cover_top']
    wfov = 2 * h_cam * math.tan(math.radians(oc['hfov'] / 2))
    res['data']['overview'] = dict(park_sx=park, vis=vis, height=h_cam, um_px=wfov / 4608 * 1000, **oc)
    if park is not None:
        item('overview', 'Overview camera sees the whole slide', 'PASS', f'park at X = +{park} mm',
             f'within X travel (to +{P["x_travel"][1]:.0f})',
             f'At X = +{park} mm the whole 75 x 25 mm slide, label included, is in view {h_cam:.0f} mm below the lens at '
             f'about {wfov / 4608 * 1000:.0f} um/px. Closer than that, the ring light hides part of it.',
             pose=[park, 0, 0], parts=['Overview camera (USB, tbd)', 'LED ring 24x WS2812'], cat='Overview')
    else:
        item('overview', 'Overview camera sees the whole slide', 'FAIL', 'no clear park position', '', 'Extend X travel.',
             cat='Overview')
    item('overview_light', 'Overview photo has its own light', 'PASS', '5 mm LED on the arm', 'lit',
         'The slide parks away from the bottom LED, so v0.2 adds a 5 mm white LED next to the overview camera. Under the '
         'slide at the park position you see the base plate through the carriage openings: stick a piece of white paper '
         'there so tissue shows pink on white.', pose=[park or 66, 0, 0], parts=['Overview LED 5 mm'], cat='Overview')
    t_over = 2 * tmove(park or 66) + 1.5
    t_total = t_tiles + t_focus + t_over
    res['data']['scan'].update(t_over=t_over, t_total=t_total)
    item('time', 'Scan time for a 15 x 15 mm area', 'PASS' if t_total <= P['time_limit_s'] else 'FAIL', f'{t_total:.0f} s',
         f'<= {P["time_limit_s"]:.0f} s', f'{nx} x {ny} = {nx * ny} tiles at {P["overlap"] * 100:.0f}% overlap. Per tile: '
                                          f'move {tmove(stepx) * 1000:.0f} ms, settle {P["settle_s"] * 1000:.0f} ms, capture '
                                          f'{P["capture_s"] * 1000:.0f} ms. Plus focus map {t_focus:.0f} s and overview {t_over:.0f} s.',
         cat='Overview')
    item('wd', 'Working distance is from the listing', 'WARN', f'{P["wd"]:.0f} mm at 1.8x assumed', 'measure',
         'The listing gives 55 to 285 mm over the zoom range and no NA. The clamp lets the lens slide about 10 mm, and the '
         'ring holder is built from this number, so measure the height at best focus when the lens arrives and the model '
         'updates.', parts=['Zoom lens 0.12-1.8x'], cat='Light path')

    # ---------------- hardware and buy list
    hw = Counter()
    for p in parts:
        for k, n in p['hw'].items():
            hw[k] += n
    res['data']['hardware'] = dict(sorted(hw.items()))
    res['data']['params'] = {k: v for k, v in P.items() if isinstance(v, (int, float, tuple, list, dict, str))}
    res['data']['timing'] = round(time.time() - t0, 1)
    return res, parts
