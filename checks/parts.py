# checks for one printed part on its own: solid, envelope, interface holes, bed size, supports, spec version
from cadquery import Vector as V
from argus.spec import P, IF, CONTRACTS, SPEC_VERSION
from argus.printing import oriented
from argus import inputs as INP
from argus.spec import FACTS

AX = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}
KIND_D = {'insert': 'insert_d', 'clearance': 'm3_clear_d'}


def holes_for(key):
    # every interface hole this part must have: (interface name, centre, unit dir, depth, diameter)
    out = []
    for name, f in IF.items():
        h = f['holes'].get(key)
        if not h:
            continue
        ax = f['axis']
        d = h.get('d', f.get('d', P[KIND_D[h['kind']]] if h['kind'] in KIND_D else None))
        pts = f['pattern'] if 'only' not in h else [f['pattern'][i] for i in h['only']]
        u = [c * h['dir'] for c in AX[ax]]
        for a, b in pts:
            c = {'x': (h['plane'], a, b), 'y': (a, h['plane'], b), 'z': (a, b, h['plane'])}[ax]
            out.append((name, c, u, h['depth'], d))
    return out


def _perp(u):
    # two unit vectors across the hole axis
    if abs(u[2]) > 0.5:
        return (1, 0, 0), (0, 1, 0)
    if abs(u[1]) > 0.5:
        return (1, 0, 0), (0, 0, 1)
    return (0, 1, 0), (0, 0, 1)


def hole_ok(shape, c, u, depth, d):
    # open: axis and 4 points just inside the wall are empty along the depth
    # present: material right around the hole at mid depth, so the hole is really in this part
    p1, p2 = _perp(u)
    ri, ro = max(d / 2 - 0.3, 0.2), d / 2 + 1.0
    dirs = [(p1, 1), (p1, -1), (p2, 1), (p2, -1)]
    for t in (0.4, depth / 2, depth - 0.4):
        base = [c[i] + u[i] * t for i in range(3)]
        probes = [base] + [[base[i] + s * q[i] * ri for i in range(3)] for q, s in dirs]
        if any(shape.isInside(V(*pt), 0.001) for pt in probes):
            return False, f'blocked {t:.1f} mm in'
    found = False
    for t in (0.4, depth / 2, depth - 0.4):
        base = [c[i] + u[i] * t for i in range(3)]
        for r in (ro, ro + 1.5):
            if any(shape.isInside(V(*[base[i] + s * q[i] * r for i in range(3)]), 0.001) for q, s in dirs):
                found = True
                break
        if found:
            break
    if not found:
        return False, 'no material around it (hole not in this part, or part moved)'
    return True, 'open'


def run(rec, support_report=None):
    key, shape = rec['key'], rec['shape']
    items = []

    def item(id_, title, status, value, detail):
        items.append(dict(id=f'{key}.{id_}', part=key, title=title, status=status, value=value, detail=detail))

    c = CONTRACTS.get(key)
    if c is None:
        item('contract', 'Has a contract', 'FAIL', 'missing', 'Add an entry for this part to spec/contracts.yaml (integrator).')
        return items
    solids = shape.Solids()
    ok = shape.isValid() and len(solids) == 1
    item('solid', 'One valid solid', 'PASS' if ok else 'FAIL', f'{len(solids)} solid(s), valid={shape.isValid()}',
         'A printed part must be one closed piece. Several solids usually means a feature floats or a cut split it.')
    bb = shape.BoundingBox()
    x0, x1, y0, y1, z0, z1 = c['envelope']
    out = [n for n, v, lo, hi in (('x', (bb.xmin, bb.xmax), x0, x1), ('y', (bb.ymin, bb.ymax), y0, y1),
                                  ('z', (bb.zmin, bb.zmax), z0, z1)) if v[0] < lo - 0.05 or v[1] > hi + 0.05]
    item('envelope', 'Stays inside its envelope', 'FAIL' if out else 'PASS',
         'outside in ' + ', '.join(out) if out else 'inside',
         f'Part spans x {bb.xmin:.1f}..{bb.xmax:.1f}, y {bb.ymin:.1f}..{bb.ymax:.1f}, z {bb.zmin:.1f}..{bb.zmax:.1f}; '
         f'envelope {c["envelope"]}. Need more room? Open a change request instead of editing the contract.')
    by_if = {}
    for name, cc, u, depth, d in holes_for(key):
        good, why = hole_ok(shape, cc, u, depth, d)
        by_if.setdefault(name, []).append((good, why, cc))
    for name, res in by_if.items():
        bad = [(why, cc) for good, why, cc in res if not good]
        item(f'if.{name}', f'Interface {name}', 'FAIL' if bad else 'PASS', f'{len(res) - len(bad)}/{len(res)} holes',
             IF[name]['about'] + ('. Problems: ' + '; '.join(f'at {tuple(round(v, 1) for v in cc)} {why}' for why, cc in bad)
                                  if bad else ''))
    s = oriented(shape, rec['orient'])
    ob = s.BoundingBox()
    bx, by_, bz = P['bed']
    fits = (ob.xlen <= bx and ob.ylen <= by_ and ob.zlen <= bz) or (ob.ylen <= bx and ob.xlen <= by_ and ob.zlen <= bz)
    item('bed', 'Fits the printer bed', 'PASS' if fits else 'FAIL', f'{ob.xlen:.0f} x {ob.ylen:.0f} x {ob.zlen:.0f} mm',
         f'Bed {bx:.0f} x {by_:.0f} x {bz:.0f} mm, in its print orientation ({rec["orient"]}).')
    if support_report:
        _, bad = support_report(shape, rec['orient'])
        item('supports', 'Prints without supports', 'WARN' if bad else 'PASS', f'{len(bad)} overhang area(s)' if bad else 'none',
             'Downward faces flatter than 42 degrees wider than 4 mm and longer than 12 mm need supports. '
             'Change the print orientation in META or add a 45 degree chamfer.' + (f' Areas: {bad[:3]}' if bad else ''))
    keys = INP.inputs_of(rec)
    stt, un = INP.state(key, keys)
    if stt == 'provisional':
        det = ('Uses facts that are not verified yet: ' + ', '.join(f"{i} ({FACTS[i]['status']})" for i in un) +
               '. Verify them first (verify issues), then the part gets a re-check task.')
        item('inputs', 'Inputs verified', 'WARN', 'provisional', det)
    elif stt == 're-check':
        item('inputs', 'Inputs verified', 'WARN', 'needs re-check',
             'Every input is verified, but the part was not re-checked against these values yet. Do the re-check task, '
             f'then run `python tools/audit.py --confirm {key}`.')
    else:
        item('inputs', 'Inputs verified', 'PASS', 'confirmed', 'Re-checked against the current verified facts.')
    st = c.get('built_for_spec', 0)
    item('spec', 'Built for the current spec', 'PASS' if st == SPEC_VERSION else 'WARN', f'spec {st}, now {SPEC_VERSION}',
         'The spec changed since this part was last checked. Re-check its interfaces, then the integrator bumps built_for_spec.')
    return items


def run_test_print(key, mod, support_report=None):
    # test prints only need to be one solid, fit the bed and print without supports
    items = []
    meta = mod.META
    shape = mod.build()
    shape = shape[0] if isinstance(shape, tuple) else shape

    def item(id_, title, status, value, detail):
        items.append(dict(id=f'test_prints.{key}.{id_}', part=key, title=title, status=status, value=value, detail=detail))

    solids = shape.Solids()
    ok = shape.isValid() and len(solids) == 1
    item('solid', 'One valid solid', 'PASS' if ok else 'FAIL', f'{len(solids)} solid(s)', 'A test print must be one piece.')
    s = oriented(shape, meta.get('orient', 'zmin'))
    ob = s.BoundingBox()
    bx, by_, bz = P['bed']
    fits = (ob.xlen <= bx and ob.ylen <= by_ and ob.zlen <= bz) or (ob.ylen <= bx and ob.xlen <= by_ and ob.zlen <= bz)
    item('bed', 'Fits the printer bed', 'PASS' if fits else 'FAIL', f'{ob.xlen:.0f} x {ob.ylen:.0f} x {ob.zlen:.0f} mm', '')
    if support_report:
        _, bad = support_report(shape, meta.get('orient', 'zmin'))
        item('supports', 'Prints without supports', 'WARN' if bad else 'PASS', f'{len(bad)} overhang area(s)' if bad else 'none',
             'Downward faces flatter than 42 degrees need supports.')
    return items
