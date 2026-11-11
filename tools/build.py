# builds the outputs into build/: 3d viewer, step assembly, oriented stl print pack, base drilling template
#   python tools/build.py            viewer only (needs build/checks.json from tools/check.py)
#   python tools/build.py --files    also step, stl print pack and drilling template
import json, base64, os, pathlib, sys, time, zipfile
from collections import Counter, defaultdict
import numpy as np
import cadquery as cq
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from argus import registry as model
from argus import bom as SHOP
from argus.spec import P, META
from argus.printing import mass_of, oriented, ORIENT_TXT
from argus.geo import box

LAYERS, CATS = META['layers'], META['cats']
STEPS = [(s['title'], s['text']) for s in META['steps']]
OUT = str(ROOT / 'build')
BUILT = time.strftime('%d %b %Y')
BUY_UNITS = {'rod': 4, 'T8 screw': 1, 'slide': 1}
LABEL = {'NEMA17': 'NEMA17 stepper 17HS4401', 'T8 screw': 'T8 lead screw 400 mm, 8 mm lead', 'T8 nut': 'T8 anti-backlash spring nut',
         'coupling': 'Flexible coupling 5 x 8 mm', '608': '608ZZ ball bearing', 'rod': '8 mm hardened rod, 250 mm',
         'LM8UU': 'LM8UU linear bearing', 'endstop': 'Optical endstop', 'BYJ': '28BYJ-48 stepper + ULN2003',
         'M4 rod': 'M4 threaded rod 100 mm', 'LED': '3 W LED on star PCB', 'diffuser': 'Opal acrylic diffuser 28 mm',
         'heatsink': 'Heatsink 20 x 20 mm', 'ring': 'WS2812 24-LED ring', 'base': 'Plywood base 300 x 270 x 18 mm',
         'feet': 'Rubber feet', 'HQ': 'Raspberry Pi HQ Camera', 'lens': 'Waveshare zoom lens 0.12-1.8x',
         'Pi': 'Raspberry Pi 3B+', 'Uno': 'Arduino Uno + CNC Shield V3', 'cam3': 'Overview USB camera (tbd)',
         'slide': 'Glass slides (50) + coverslips', 'led5': '5 mm white LED'}
def b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def mesh_data(shape, tol=0.08, ang=0.35):
    v, t = shape.tessellate(tol, ang)
    pos = np.array([[p.x, p.y, p.z] for p in v], dtype=np.float64)
    q = np.round(pos * 100).astype(np.int16)
    idx = np.array(t, dtype=np.uint32).ravel()
    big = len(pos) > 65535
    return dict(v=b64(q), i=b64(idx if big else idx.astype(np.uint16)), i32=big, nv=len(pos), nt=len(t))


def buy_key(p):
    return p['buy']


def drilling_template(parts, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    W, H = 420.0, 297.0
    bx0, bx1, by0, by1 = P['base']
    ox, oy = W - 8 - bx1, (H - (by1 - by0)) / 2 - by0
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect('equal')
    ax.axis('off')
    T = lambda x, y: (x + ox, y + oy)
    ax.add_patch(Rectangle(T(bx0, by0), bx1 - bx0, by1 - by0, fill=False, lw=0.8, ec='black'))
    for p in parts:
        if p['group'] != 'F' or p['cat'] != 'printed':
            continue
        bb = p['shape'].BoundingBox()
        if bb.zmin > 0.5:
            continue
        sl = p['shape'].intersect(box(bx0 - 50, bx1 + 50, by0 - 50, by1 + 50, -0.1, 0.6))
        sb = sl.BoundingBox()
        ax.add_patch(Rectangle(T(sb.xmin, sb.ymin), sb.xlen, sb.ylen, fill=False, lw=0.4, ec='#777777', ls='--'))
        ax.text(*T(sb.xmin + 1.5, sb.ymax - 4), p['name'], fontsize=5.5, color='#555555', va='top')
    n = 0
    for p in parts:
        for x, y, lab in p['holes']:
            X, Y = T(x, y)
            below = 'below' in lab
            ax.add_patch(Circle((X, Y), 2.15, fill=False, lw=0.6, ec='#c0392b' if not below else '#2c6fbb',
                                ls='-' if not below else ':'))
            ax.plot([X - 4, X + 4], [Y, Y], lw=0.35, color='black')
            ax.plot([X, X], [Y - 4, Y + 4], lw=0.35, color='black')
            n += 1
    X0, Y0 = T(0, 0)
    ax.plot([X0 - 12, X0 + 12], [Y0, Y0], lw=0.5, color='#5a3ea6')
    ax.plot([X0, X0], [Y0 - 12, Y0 + 12], lw=0.5, color='#5a3ea6')
    ax.text(X0 + 2, Y0 + 2, 'optical axis', fontsize=5.5, color='#5a3ea6')
    ax.text(*T((bx0 + bx1) / 2, by0 - 3), 'FRONT (user side)', fontsize=7, va='top', ha='center')
    ax.text(*T((bx0 + bx1) / 2, by1 + 2), 'BACK (column side)', fontsize=7, va='bottom', ha='center')
    import textwrap
    txt = [f'ARGUS T18', f'base drilling template {P["version"]}', f'1:1, plate {bx1 - bx0:.0f} x {by1 - by0:.0f} mm', '',
           *textwrap.wrap('Print on A3 at 100 % (actual size, no fit to page). The bar on the right of this text must be '
                          'exactly 100 mm.', 30), '',
           *textwrap.wrap('Align the outline with the plate edges and tape it down. Punch every red cross and pre-drill '
                          '2.5 mm for 4 mm wood screws (or drill 3.3 and tap M4 in aluminium).', 30), '',
           *textwrap.wrap('Blue dotted circles are the rubber feet: drill those from below.', 30), '',
           *textwrap.wrap('Dashed boxes show where each printed part sits.', 30), '', f'{n} holes, all relative to the optical axis.']
    ax.text(8, H - 10, '\n'.join(txt), fontsize=7.5, va='top', ha='left', linespacing=1.35)
    ax.plot([96, 96], [40, 140], lw=1.6, color='black')
    for yy in (40, 140):
        ax.plot([93, 99], [yy, yy], lw=0.8, color='black')
    ax.text(92, 90, '100 mm', fontsize=7, ha='right', va='center', rotation=90)
    fig.savefig(path)
    plt.close(fig)
    return n


SHOP_BY_KEY = {r['key']: r for r in SHOP.rows()}
# price per modelled piece when the bought unit is a pack or shared stock
PIECE = {
    'LM8UU (X)': (49.99, 'from the PRC 10-pack, 499.90 TL'), 'LM8UU (Y)': (49.99, 'from the PRC 10-pack, 499.90 TL'),
    'LM8UU (Z)': (49.99, 'from the PRC 10-pack, 499.90 TL'),
    'X rod': (94.50, 'one full 250 mm rod, cut to 219 mm'),
    'Y rod': (47.25, 'half a 250 mm rod (Y 108 + Z 100 from one rod)'), 'Z rod': (47.25, 'half a 250 mm rod (Y 108 + Z 100 from one rod)'),
    'X lead screw': (315.31, 'share of one 466.50 TL screw (X 196 mm + Y 94 mm)'),
    'Y lead screw': (151.19, 'share of one 466.50 TL screw (X 196 mm + Y 94 mm)'),
    'Glass slide': (4.0, 'from a 200 TL pack of 50 slides + coverslips'),
}


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    parts = model.build()
    checks = json.load(open(f'{OUT}/checks.json'))
    pinfo = checks['data']['print']
    plist = []
    for k, p in enumerate(parts):
        md = mesh_data(p['shape'])
        bb = p['shape'].BoundingBox()
        bk = buy_key(p)
        rec = dict(id=k, name=p['name'], group=p['group'], layer=p['layer'], cat=p['cat'], sub=p['sub'], step=p['step'],
                   color=p['color'], mass=round(mass_of(p), 1), note=p['note'], hw=p['hw'],
                   size=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)], **md)
        if bk:
            r = SHOP_BY_KEY[SHOP.PART_KEY[bk]]
            rec['buy'] = dict(key=r['key'], item=r['item'], store=r['store'], url=r['url'], unit=r['unit'], status=r['status'], note=r['note'])
            pc = PIECE.get(p['name'])
            if pc:
                rec['buy']['piece'], rec['buy']['piece_note'] = pc
        if p['cat'] == 'printed':
            rec['pr'] = pinfo[p['name']]
        plist.append(rec)
    hw = checks['data']['hardware']
    shop = SHOP.rows()
    data = dict(parts=plist, layers=LAYERS, cats=CATS, steps=[dict(title=a, text=b) for a, b in STEPS], checks=checks,
                params={k: v for k, v in P.items() if isinstance(v, (int, float, tuple, list, dict, str))},
                shop=shop, hw=hw, budget_tl=SHOP.BUDGET_TL, pla_tl_g=0.671, redesign=SHOP.REDESIGN, status_txt=SHOP.STATUS_TXT, built=BUILT, version=P['version'])
    js = json.dumps(data, separators=(',', ':'))
    html = open(ROOT / 'tools' / 'viewer_template.html').read().replace('/*__DATA__*/null', js)
    open(f'{OUT}/argus-viewer.html', 'w').write(html)
    print('viewer', round(len(html) / 1e6, 2), 'MB')
    tot = {s: sum(r['total'] for r in shop if r['status'] == s) for s in SHOP.STATUS_TXT}
    print('shop totals', tot, 'sum', sum(tot.values()))

    if '--files' in sys.argv:
        v = P['version']
        assy = cq.Assembly(name=f'ARGUS_T18_{v}')
        for k, p in enumerate(parts):
            c = p['color'].lstrip('#')
            col = cq.Color(int(c[0:2], 16) / 255, int(c[2:4], 16) / 255, int(c[4:6], 16) / 255)
            nm = f"{k:02d}_{p['name']}"
            for a, b in ((' ', '_'), ('/', '-'), ('(', ''), (')', ''), ('+', 'and'), (',', ''), ('.', '')):
                nm = nm.replace(a, b)
            assy.add(p['shape'], name=nm, color=col)
        assy.save(f'{OUT}/ARGUS_T18_scanner_{v}.step')
        print('step done')
        os.makedirs(f'{OUT}/stl_{v}', exist_ok=True)
        zpath = f'{OUT}/ARGUS_T18_print_pack_{v}.zip'
        done = {}
        for p in parts:
            if p['cat'] != 'printed' or p['name'] in done:
                continue
            fn = p['name'].replace(' ', '_').replace('(', '').replace(')', '').replace(',', '') + '.stl'
            cq.exporters.export(oriented(p['shape'], p['orient']), f'{OUT}/stl_{v}/{fn}', tolerance=0.02,
                                angularTolerance=0.12)
            done[p['name']] = (fn, p)
        order = sorted(done.items(), key=lambda kv: (kv[1][1]['step'], kv[0]))
        lines = [f'ARGUS T18 print pack {v} ({BUILT})', '',
                 'Every STL is already rotated into its print orientation and sits on the bed at z = 0. No supports needed.',
                 'Default: PLA+ or PETG, 0.2 mm layers, 4 walls, 5 top/bottom layers, 40% gyroid infill.',
                 'Lens clamp and ring holder: black PLA. LED tower: white PLA. Slide holder: 0.12 mm layers.',
                 'Holes are printed at nominal size + clearance: M3 3.4 mm, heat-set inserts 4.0 mm, LM8UU saddles 15.1 mm,',
                 'rods 8.1 mm, 608 seats 22.15 mm. If your printer prints holes small, scale nothing; drill or ream instead.',
                 'Print one LM8UU saddle test first (the X carriage corner) if you are unsure about your printer.', '',
                 'step, file, qty, size on bed (mm), filament (g), time (h, rough), orientation']
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            tg = th = 0
            for name, (fn, p) in order:
                info = pinfo[name]
                z.write(f'{OUT}/stl_{v}/{fn}', fn)
                d = info['dims']
                lines.append(f'{p["step"]}, {fn}, {info["qty"]}, {d[0]:.0f} x {d[1]:.0f} x {d[2]:.0f}, '
                             f'{info["grams"] * info["qty"]:.0f}, {info["hours"] * info["qty"]:.1f}, {info["orient"]}')
                tg += info['grams'] * info['qty']
                th += info['hours'] * info['qty']
            lines += ['', f'Total about {tg:.0f} g of filament and {th:.0f} h of printing.', '',
                      'Screws, inserts and small parts for the whole scanner:']
            lines += [f'  {n} x {k}' for k, n in hw.items()]
            z.writestr('README.txt', '\n'.join(lines) + '\n')
        print('print pack', len(done), 'parts')
        n = drilling_template(parts, f'{OUT}/ARGUS_T18_base_drilling_template_{v}_A3.pdf')
        print('template', n, 'holes')
    print('export', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
