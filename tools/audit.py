# uncertainty audit: which facts are unverified, which parts depend on them, what to do next
#   python tools/audit.py                     print the status
#   python tools/audit.py --md build/status.md
#   python tools/audit.py --confirm lens_clamp   after a re-check: store the current inputs hash in contracts.yaml
#   python tools/audit.py --sync              (ci, needs gh) open and close verify and re-check issues, mark design
#                                             issues waiting while their part is provisional, update the status board
import argparse, json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from argus import registry
from argus import inputs as INP
from argus.spec import FACTS, VERIFIED, CONTRACTS

MARK = '<!-- argus-audit -->'
ALWAYS = {'printer': 'the checks (bed size)'}   # facts used by the checks, not by a shape
STATE_TXT = {'provisional': 'provisional', 're-check': 'needs re-check', 'confirmed': 'confirmed'}


def collect():
    parts = registry.build()
    printed = {p['key']: p for p in parts if p['cat'] == 'printed'}
    used = {}       # fact item -> set of printed part keys
    bought = {}     # fact item -> set of bought part names
    rows = {}
    for k, p in printed.items():
        keys = INP.inputs_of(p)
        st, un = INP.state(k, keys)
        rows[k] = dict(state=st, unverified=un, keys=keys, hash=INP.inputs_hash(keys), name=p['name'], module=p['module'])
        for key in keys:
            used.setdefault(key.split('.')[0], set()).add(k)
    for p in parts:
        if p['cat'] != 'printed':
            for key in p['facts']:
                bought.setdefault(key.split('.')[0], set()).add(p['name'])
    return rows, used, bought


def status_md(rows, used, bought, links=None):
    links = links or {}
    nf = len(FACTS)
    nv = sum(1 for f in FACTS.values() if f['status'] in VERIFIED)
    cnt = {s: sum(1 for r in rows.values() if r['state'] == s) for s in STATE_TXT}
    L = [MARK, '# ARGUS status board', '',
         f"Updated by the audit. Facts verified: **{nv} of {nf}**. Printed parts: **{cnt['confirmed']} confirmed**, "
         f"**{cnt['re-check']} need a re-check**, **{cnt['provisional']} provisional** (built on unverified facts).", '',
         'How it works: verify a fact (measure it or find the datasheet) and every part that uses it moves on; when all '
         'inputs of a part are verified it gets a re-check task; after the re-check it is confirmed. Rules: REHBER.md.', '',
         '## Verify these first', '', '| Fact | Status | Parts waiting on it | Task |', '|---|---|---|---|']
    todo = [i for i, f in FACTS.items() if f['status'] not in VERIFIED]
    todo.sort(key=lambda i: -len(used.get(i, ())))
    for i in todo:
        parts = ', '.join(sorted(used.get(i, ()))) or ('bought parts only: ' + ', '.join(sorted(bought.get(i, ()))) if bought.get(i) else ALWAYS.get(i, 'not used yet'))
        L.append(f"| `{i}`: {FACTS[i]['item']} | {FACTS[i]['status']} | {parts} | {links.get(('verify', i), '')} |")
    L += ['', '## Parts', '', '| Part | State | Waiting on | Task |', '|---|---|---|---|']
    order = {'re-check': 0, 'provisional': 1, 'confirmed': 2}
    for k, r in sorted(rows.items(), key=lambda kv: (order[kv[1]['state']], kv[1]['module'], kv[0])):
        L.append(f"| `{k}` | {STATE_TXT[r['state']]} | {', '.join(r['unverified'])} | {links.get(('re-check', k), '')} |")
    L += ['', '## How the facts connect to the parts', '', '```mermaid', 'graph LR']
    for i in FACTS:
        if i in used:
            cls = 'ok' if FACTS[i]['status'] in VERIFIED else 'bad'
            L.append(f'  f_{i}["{i}<br/>{FACTS[i]["status"]}"]:::{cls}')
    for k, r in rows.items():
        cls = {'confirmed': 'ok', 're-check': 'todo', 'provisional': 'wait'}[r['state']]
        L.append(f'  p_{k}(["{k}"]):::{cls}')
    for i, ks in used.items():
        for k in sorted(ks):
            L.append(f'  f_{i} --> p_{k}')
    L += ['  classDef ok fill:#dcefe4,stroke:#23744a', '  classDef bad fill:#f8d7d3,stroke:#c62f2f',
          '  classDef todo fill:#f5e8cf,stroke:#915c10', '  classDef wait fill:#e3e6ef,stroke:#4a5170', '```', '']
    return '\n'.join(L)


def verify_body(item, used, bought):
    f = FACTS[item]
    vals = '\n'.join(f'- `{k}` = {v}' for k, v in f['values'].items())
    parts = ', '.join(f'`{k}`' for k in sorted(used.get(item, ()))) or 'none yet'
    bparts = ', '.join(sorted(bought.get(item, ()))) or 'none'
    extra = ''
    if item == 'printer_fit':
        extra = '\nThis one is done by printing the fit coupons (see the test-print task) and noting which size fits each real part.\n'
    return f"""{MARK}
# Verify: {f['item']}

The 3D design uses these numbers, but today they are only **{f['status']}** (`{f['evidence']}`). Until they are verified, every part that uses them is provisional and its design task waits.
{extra}
**Current values** (`spec/facts.yaml`, item `{item}`):
{vals}

**Printed parts that depend on it:** {parts}
**Bought part shapes that use it:** {bparts}

## How to verify
Either way works, the first is best:
1. **Measure our own part:** calipers. Take a photo with a ruler or the caliper in view. Status `measured`.
2. **Find the maker's datasheet or drawing,** not a shop page. Status `datasheet`.

Then, in one pull request:
- Put the photo or PDF in `evidence/{item}/`, or a link in `evidence`.
- In `spec/facts.yaml` under `{item}`, update `values` (add any value that is missing; keep the names), `status`, `evidence`, and add `by: <your name>` and `date: <today>`.
- Run `python tools/check.py` if you can. Parts may now fail because a real size differs: that is the point. Say so in the pull request, and the re-check tasks will fix them.

Any AI with web search can do the datasheet route; paste this issue into it. The measuring route needs the part in hand.
"""


def gh(*args):
    r = subprocess.run(['gh', *args], capture_output=True, text=True)
    if r.returncode:
        print('gh', ' '.join(args[:3]), '->', r.stderr.strip()[:200])
    return r


def sync(rows, used, bought):
    for name, color in (('verify', '0e8a16'), ('re-check', 'fbca04'), ('waiting', 'bfbfbf'), ('status', '5319e7')):
        gh('label', 'create', name, '--color', color, '--force')
    issues = json.loads(gh('issue', 'list', '--state', 'all', '--limit', '500', '--json',
                           'number,title,state,labels,body').stdout or '[]')
    by_title = {}
    for i in issues:
        by_title.setdefault(i['title'], i)
    links = {}

    def ensure(title, body, labels, want_open, kind, key):
        cur = by_title.get(title)
        tmp = ROOT / 'build' / 'audit_body.md'
        tmp.parent.mkdir(exist_ok=True)
        if want_open:
            tmp.write_text(body, encoding='utf-8')
            if cur is None:
                args = ['issue', 'create', '--title', title, '--body-file', str(tmp)]
                for lab in labels:
                    args += ['--label', lab]
                r = gh(*args)
                url = r.stdout.strip()
                links[(kind, key)] = f"#{url.rsplit('/', 1)[-1]}" if url else ''
                print('opened', title)
            else:
                links[(kind, key)] = f"#{cur['number']}"
                if cur['state'] == 'CLOSED':
                    gh('issue', 'reopen', str(cur['number']))
                if cur['body'].strip() != body.strip():
                    gh('issue', 'edit', str(cur['number']), '--body-file', str(tmp))
        elif cur is not None and cur['state'] == 'OPEN':
            gh('issue', 'close', str(cur['number']), '--comment', 'Closed by the audit: done.')
            print('closed', title)

    for item in FACTS:
        unv = FACTS[item]['status'] not in VERIFIED
        relevant = item in used or item in bought or item in ALWAYS
        ensure(f"[verify] {item}: {FACTS[item]['item']}", verify_body(item, used, bought), ['verify'],
               unv and relevant, 'verify', item)
    for k, r in rows.items():
        want = r['state'] == 're-check'
        title = f'[re-check] {k}: redo against verified inputs'
        body = ''
        if want:
            goal = (f'Every fact this part uses is now verified. Do not trust the current design: check every feature against '
                    f'the verified facts, the contract and the neighbouring parts, and redesign what is wrong or weak. When it '
                    f'passes, run `python tools/audit.py --confirm {k}` and include the contracts.yaml change in the pull request.')
            body = subprocess.run([sys.executable, str(ROOT / 'tools' / 'task.py'), k, '--goal', goal, '--who', 'Any strong AI'],
                                  capture_output=True, text=True).stdout
            body = MARK + '\n' + body.split('\n---\n', 1)[-1]
        ensure(title, body, ['re-check', 'design'], want, 're-check', k)
    # design issues wait while their part is provisional
    for i in issues:
        if i['state'] != 'OPEN':
            continue
        labs = {l['name'] for l in i['labels']}
        if 'design' not in labs or 're-check' in labs:
            continue
        m = re.search(r'\*\*Part:\*\* `([\w]+)`', i['body'] or '')
        if not m or m.group(1) not in rows:
            continue
        r = rows[m.group(1)]
        if r['state'] == 'provisional':
            todo = ', '.join(f"`{u}` {links.get(('verify', u), '')}".strip() for u in r['unverified'])
            msg = (f'{MARK}\n**Waiting on facts.** This part still uses unverified numbers: {todo}. Verify those first '
                   f'(measure or datasheet, see the verify issues), then start here. The audit updates this comment.')
            if 'waiting' not in labs:
                gh('issue', 'edit', str(i['number']), '--add-label', 'waiting')
        else:
            msg = f'{MARK}\n**Inputs verified.** Every fact this part uses is verified, go ahead.'
            if 'waiting' in labs:
                gh('issue', 'edit', str(i['number']), '--remove-label', 'waiting')
        cm = json.loads(gh('api', f"repos/{{owner}}/{{repo}}/issues/{i['number']}/comments").stdout or '[]')
        old = [c for c in cm if MARK in (c.get('body') or '')]
        if old:
            if old[-1]['body'].strip() != msg.strip():
                gh('api', '-X', 'PATCH', f"repos/{{owner}}/{{repo}}/issues/comments/{old[-1]['id']}", '-f', f'body={msg}')
        else:
            gh('issue', 'comment', str(i['number']), '--body', msg)
    # status board
    md = status_md(rows, used, bought, links)
    tmp = ROOT / 'build' / 'status.md'
    tmp.write_text(md, encoding='utf-8')
    board = [i for i in issues if i['title'] == 'Status board']
    if board:
        if board[0]['state'] == 'CLOSED':
            gh('issue', 'reopen', str(board[0]['number']))
        gh('issue', 'edit', str(board[0]['number']), '--body-file', str(tmp))
    else:
        gh('issue', 'create', '--title', 'Status board', '--label', 'status', '--body-file', str(tmp))
    return md


def confirm(key, rows):
    r = rows[key]
    if r['state'] == 'provisional':
        sys.exit(f"{key} still uses unverified facts ({', '.join(r['unverified'])}); verify them first")
    p = ROOT / 'spec' / 'contracts.yaml'
    s = p.read_text(encoding='utf-8')
    m = re.search(rf'^{re.escape(key)}:\n((?:  .*\n|    .*\n)*)', s, re.M)
    if not m:
        sys.exit(f'{key} not in contracts.yaml')
    block = m.group(0)
    nb = re.sub(r"  confirmed_inputs: .*\n", f"  confirmed_inputs: '{r['hash']}'\n", block) if 'confirmed_inputs' in block \
        else block.replace('\n', f"\n  confirmed_inputs: '{r['hash']}'\n", 1)
    p.write_text(s.replace(block, nb), encoding='utf-8')
    print(f"{key} confirmed against inputs {r['hash']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md')
    ap.add_argument('--sync', action='store_true')
    ap.add_argument('--confirm')
    a = ap.parse_args()
    rows, used, bought = collect()
    if a.confirm:
        return confirm(a.confirm, rows)
    md = sync(rows, used, bought) if a.sync else status_md(rows, used, bought)
    if a.md:
        pathlib.Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.md).write_text(md, encoding='utf-8')
    cnt = {s: sum(1 for r in rows.values() if r['state'] == s) for s in STATE_TXT}
    print(f"facts verified {sum(1 for f in FACTS.values() if f['status'] in VERIFIED)}/{len(FACTS)}; parts "
          f"confirmed {cnt['confirmed']}, re-check {cnt['re-check']}, provisional {cnt['provisional']}")
    for k, r in sorted(rows.items()):
        print(f"  {STATE_TXT[r['state']]:<15} {k:<22} {', '.join(r['unverified'])}")


if __name__ == '__main__':
    main()
