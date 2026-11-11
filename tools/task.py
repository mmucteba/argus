# writes a self-contained task prompt for one printed part, ready to paste into a github issue or any ai chat
#   python tools/task.py led_tower --goal "fit the real led card" --inputs "card 23 x 30 mm, holes 2.2 mm at ..."
#   python tools/task.py led_tower --out build/task_led_tower.md
import argparse, importlib, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from argus.spec import P, IF, CONTRACTS, SPEC_VERSION
from argus.registry import find_module
from argus.printing import ORIENT_TXT

GROUPS = {'F': 'nothing (fixed to the base)', 'X': 'the X carriage', 'Y': 'the Y carriage (on top of X)',
          'Z': 'the focus carriage'}

REPO = 'https://github.com/mmucteba/argus/blob/main'


def neighbours(key, margin=3.0):
    a = CONTRACTS[key]['envelope']
    out = []
    for k, c in CONTRACTS.items():
        b = c['envelope']
        if k != key and all(a[2 * i] - margin < b[2 * i + 1] and b[2 * i] - margin < a[2 * i + 1] for i in range(3)):
            out.append(f"{c['name']} (`{k}`, envelope {b})")
    return out


def interface_lines(key):
    lines = []
    for name, f in IF.items():
        if key not in f['holes']:
            continue
        h = f['holes'][key]
        pts = f['pattern'] if 'only' not in h else [f['pattern'][i] for i in h['only']]
        others = [p for p in f['holes'] if p != key]
        pts_txt = ', '.join('(' + ', '.join(f'{v:g}' for v in p) + ')' for p in pts)
        d = h.get('d', f.get('d'))
        lines.append(f"- **{name}**: {f['about']}. Axis {f['axis']}, centres {pts_txt}, starts at {f['axis']} = {h['plane']:g}, "
                     f"goes {'+' if h['dir'] > 0 else '-'}{f['axis']} at least {h['depth']:g} mm, {h['kind']}"
                     f"{f', diameter {d:g} mm' if d else ''}. Mates with: {', '.join(others) or 'a bought part'}. "
                     f"In code: `pat('{name}')`.")
    return lines or ['- none listed']


def fmt(v):
    if isinstance(v, float):
        return f'{v:.2f}'.rstrip('0').rstrip('.')
    if isinstance(v, (list, tuple)):
        return '[' + ', '.join(fmt(x) for x in v) + ']'
    return str(v)


def used_params(code):
    keys = sorted(set(re.findall(r"P\['(\w+)'\]", code)))
    return [f"- `{k}` = {fmt(P[k])}" for k in keys]


def bought_near(key, margin=3.0):
    # bought parts whose box reaches into this part's envelope, in assembled position at home
    from argus import registry
    e = CONTRACTS[key]['envelope']
    out = []
    for p in registry.build():
        if p['cat'] == 'printed':
            continue
        bb = p['shape'].BoundingBox()
        b = (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)
        if all(e[2 * i] - margin < b[2 * i + 1] and b[2 * i] - margin < e[2 * i + 1] for i in range(3)):
            out.append(f"{p['name']}: box {fmt(list(b))}" + (f" ({p['note']})" if p['note'] else ''))
    return out


def facts_lines(key):
    # real-world numbers behind this part and how sure we are about them
    from argus import registry, inputs as INP
    from argus.spec import FACTS, VERIFIED
    rec = registry.build(only=key)[0]
    keys = INP.inputs_of(rec)
    st, un = INP.state(key, keys)
    items = {}
    for k in keys:
        i, v = k.split('.', 1)
        items.setdefault(i, []).append(v)
    out = []
    for i, vs in sorted(items.items()):
        f = FACTS[i]
        ok = 'verified' if f['status'] in VERIFIED else 'NOT VERIFIED'
        vals = ', '.join(f"{v} = {fmt(f['values'][v])}" for v in vs if v != '*') or 'whole item: ' + ', '.join(
            f'{a} = {fmt(b)}' for a, b in f['values'].items())
        out.append(f"- `{i}` ({f['status']}, {ok}): {vals}. Read them as `F.{i}.<name>`.")
    if st == 'provisional':
        out += ['', f"**Stop first:** this part is provisional. {', '.join(un)} must be verified (measured or datasheet, "
                "see the issues labelled verify) before this design is final. If you go on anyway, say in your note "
                "which numbers are still unverified."]
    return out or ['- none']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('part')
    ap.add_argument('--goal', default='')
    ap.add_argument('--inputs', default='')
    ap.add_argument('--model', default='Fable or the strongest model you have')
    ap.add_argument('--also', action='append', default=[], help='other files this task may change')
    ap.add_argument('--who', help='adds an issue header: Fable (hard geometry), Any strong AI, Anyone')
    ap.add_argument('--title')
    ap.add_argument('--out')
    a = ap.parse_args()
    key = a.part
    c = CONTRACTS[key]
    mod = find_module(key)
    path = f'parts/{mod}/{key}.py'
    code = (ROOT / path).read_text()
    meta = importlib.import_module(f'parts.{mod}.{key}').META
    layout_p = ROOT / 'parts' / mod / 'layout.py'
    layout = layout_p.read_text() if layout_p.exists() and f'parts.{mod}.layout' in code else ''
    api = (ROOT / 'docs' / 'geo_api.md').read_text()
    goal = a.goal or c.get('open') or 'Improve this part.'
    L = [
        f"# Task: {c['name']}",
        '',
        f"**Suggested model:** {a.model}. **Part file:** `{path}`. **Spec version:** {SPEC_VERSION}. **Status:** {c['status']}.",
        '',
        'You are designing one 3D printed part of ARGUS T18, a low-cost automated microscope slide scanner '
        '(METU EE493 capstone). A two-axis stage moves the slide under a fixed zoom lens and Raspberry Pi HQ camera. '
        'Parts are CadQuery Python, modelled in assembled position. Many people work on different parts at the same '
        'time, so each part has a contract: a box it must stay inside and holes it must keep where other parts meet it.',
        '',
        '## Goal',
        goal,
        '',
        '## Inputs (measurements or listing data)',
        a.inputs or '- none given; use the listing values already in the code and say which numbers you assumed',
        '',
        '## Contract',
        f"- Envelope (x0, x1, y0, y1, z0, z1): {c['envelope']}. Stay inside it.",
        f"- Moves with: {GROUPS[meta['group']]}. Prints {ORIENT_TXT[meta['orient']]}.",
        '- Interface holes you must keep exactly (other parts depend on them):',
        *interface_lines(key),
        '- Parts whose space is next to yours:',
        *([f'  - {n}' for n in neighbours(key)] or ['  - none']),
        '- Bought parts in or next to your space (assembled, stage at home):',
        *([f'  - {n}' for n in bought_near(key)] or ['  - none']),
        '',
        '## Facts this part depends on',
        *facts_lines(key),
        '',
        '## Rules',
        f'1. Change only `{path}`' + ''.join(f' and `{x}`' for x in a.also) + '. Keep `META` and `build()`.',
        '2. Take numbers from `P[...]`, `pat(...)` and `F.<item>.<value>` (facts). Never type in a real-world size or a '
        'number another part depends on; if a size you need is missing from spec/facts.yaml, ask for it in a change request.',
        '3. If the goal needs a bigger envelope, a moved interface or a new parameter, do not change shared files: '
        'finish what you can and write a **change request** (what, why, the new numbers) at the end of your answer.',
        '4. Print-friendly: no supports in the chosen orientation (overhangs steeper than 45 degrees from vertical need a '
        'chamfer), walls at least 1.2 mm, fits a 220 x 220 x 250 mm bed.',
        '5. Code comments: short, lowercase, no punctuation.',
        '',
        '## Parameters this part uses now',
        *(used_params(code + layout) or ['- none']),
        '',
        '## Current code',
        f'`{path}`',
        '```python',
        code.rstrip(),
        '```',
    ]
    if layout:
        L += ['', f'`parts/{mod}/layout.py` (shared by the module, read only)', '```python', layout.rstrip(), '```']
    L += ['', api.replace('# Geometry helpers (argus.geo)', '## Geometry helpers (argus.geo)'), '',
          '## Check your work',
          f'- If you can run code: `pip install -r requirements.txt`, then `python tools/check.py {key}` (seconds) and '
          '`python tools/check.py` (whole machine, about a minute). All must pass.',
          '- If you cannot run code: deliver the file anyway; the checks run automatically on the pull request.',
          '',
          '## Deliver',
          f'1. The full new `{path}`' + ''.join(f' and `{x}`' for x in a.also) + '.',
          '2. Three lines: what changed, which numbers are measured vs assumed, what you are unsure about.',
          '3. A change request, only if rule 3 applied.',
          '',
          f'Repo: {REPO.rsplit("/blob", 1)[0]} (read everything else in CONTEXT.md if you have access).']
    txt = '\n'.join(L) + '\n'
    if a.who:
        title = a.title or f"[design] {key}: {c['name'].lower()}"
        labels = 'design' + (', fable' if a.who.startswith('Fable') else '')
        txt = f'---\ntitle: "{title}"\nlabels: {labels}\npart: {key}\nwho: {a.who}\n---\n' + txt
    if a.out:
        pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.out).write_text(txt, encoding='utf-8')
    else:
        sys.stdout.write(txt)


if __name__ == '__main__':
    main()
