# runs the checks and prints a report
#   python tools/check.py              everything: every printed part + the whole machine (a few minutes)
#   python tools/check.py lens_clamp   one part on its own (seconds)
#   --report build/report.md          also write a markdown report (ci posts it on the pull request)
#   --scope origin/main               also list files changed against a branch and flag edits outside one part folder
# exit code 1 when anything fails
import argparse, json, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from argus import registry
from argus.spec import CONTRACTS
from checks import parts as part_checks

ICON = {'PASS': 'PASS', 'WARN': 'WARN', 'FAIL': 'FAIL'}


def scope_items(base):
    try:
        out = subprocess.run(['git', 'diff', '--name-only', f'{base}...HEAD'], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.split()
    except Exception as e:
        return [dict(id='scope', part='-', title='Change scope', status='WARN', value='unknown', detail=f'git diff failed: {e}')], []
    part_dirs = sorted({'/'.join(f.split('/')[:2]) for f in out if f.startswith('parts/')})
    shared = [f for f in out if f.split('/')[0] in ('spec', 'argus', 'checks', 'tools', '.github')]
    many = len(part_dirs) > 1
    st = 'WARN' if shared or many else 'PASS'
    det = f'{len(out)} file(s) changed. Part folders: {", ".join(part_dirs) or "none"}.'
    if shared:
        det += f' Shared files changed: {", ".join(shared)}. These need the integrator: other parts depend on them.'
    if many:
        det += ' More than one part folder changed: fine for a planned change, otherwise split the pull request.'
    return [dict(id='scope', part='-', title='Change scope', status=st, value=f'{len(out)} files', detail=det)], out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('part', nargs='?')
    ap.add_argument('--report')
    ap.add_argument('--json')
    ap.add_argument('--scope')
    ap.add_argument('--no-machine', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    items, data = [], {}
    if a.scope:
        s = scope_items(a.scope)
        items += s[0]
    from checks.assembly import support_report
    if a.part:
        recs = registry.build(only=a.part)
    else:
        recs = registry.build()
    printed = [r for r in recs if r['cat'] == 'printed']
    missing = [k for k in CONTRACTS if k not in {r['key'] for r in printed}] if not a.part else []
    for k in missing:
        items.append(dict(id=f'{k}.exists', part=k, title='Part file exists', status='FAIL', value='missing',
                          detail=f'spec/contracts.yaml lists {k} but parts/{CONTRACTS[k]["module"]}/{k}.py is missing.'))
    for r in printed:
        items += part_checks.run(r, support_report)
    if not a.part and not a.no_machine:
        from checks import assembly
        res, _ = assembly.run()
        data = res['data']
        for it in res['items']:
            items.append(dict(id='machine.' + it['id'], part='machine', title=it['title'], status=it['status'],
                              value=str(it['value']), detail=it['detail']))
    for i in items:
        if i['status'] not in ('PASS', 'WARN', 'FAIL'):
            i['status'] = 'PASS'  # info lines count as pass
    n = {s: sum(1 for i in items if i['status'] == s) for s in ('PASS', 'WARN', 'FAIL')}
    for i in sorted(items, key=lambda i: ('FAIL', 'WARN', 'PASS').index(i['status'])):
        if i['status'] != 'PASS' or a.part:
            print(f"{i['status']:4}  {i['part']:<20} {i['title']}: {i['value']}")
            if i['status'] != 'PASS':
                print(f"      {i['detail']}")
    print(f"\n{n['PASS']} pass, {n['WARN']} warn, {n['FAIL']} fail  ({time.time() - t0:.0f} s)")
    if a.report:
        p = pathlib.Path(a.report)
        p.parent.mkdir(parents=True, exist_ok=True)
        verdict = 'All checks pass' if not n['FAIL'] else f"{n['FAIL']} check(s) fail"
        L = [f"## ARGUS checks: {verdict}", '', f"{n['PASS']} pass, {n['WARN']} warn, {n['FAIL']} fail.", '']
        bad = [i for i in items if i['status'] != 'PASS']
        if bad:
            L += ['| | Part | Check | Result | What to do |', '|---|---|---|---|---|']
            for i in sorted(bad, key=lambda i: ('FAIL', 'WARN').index(i['status'])):
                L.append(f"| {i['status']} | {i['part']} | {i['title']} | {i['value']} | {i['detail'].replace('|', '/')} |")
        L += ['', '<details><summary>Passing checks</summary>', '']
        L += [f"- {i['part']}: {i['title']} ({i['value']})" for i in items if i['status'] == 'PASS']
        L += ['', '</details>']
        p.write_text('\n'.join(L), encoding='utf-8')
    if a.json:
        p = pathlib.Path(a.json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dict(items=items, data=data), indent=1, default=str))
    sys.exit(1 if n['FAIL'] else 0)


if __name__ == '__main__':
    main()
