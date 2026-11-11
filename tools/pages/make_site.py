# builds the github pages site into site/: an overview page plus the verification map, 3d viewer, parts and wiring pages
# run after the checks and the other pages so it can read them:
#   python tools/check.py --report build/report.md --json build/checks.json
#   python tools/build.py && python tools/pages/make_shop_page.py && python tools/pages/make_wiring_page.py
#   python tools/pages/make_site.py
import datetime, json, os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'pages'))
import make_verification_page as V
from argus import bom as BOM
from argus.spec import P, SPEC_VERSION

SITE = ROOT / 'site'
BUILD = ROOT / 'build'
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'mmucteba/argus')
REPO = f'https://github.com/{REPO_NAME}'
PAGES = [('verification.html', 'argus-verification.html'), ('viewer.html', 'argus-viewer.html'),
         ('parts.html', 'argus-parts.html'), ('wiring.html', 'argus-wiring.html')]
HEAD = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
NAV = ('<nav style="max-width:1160px;margin:0 auto 14px;font:500 13px \'IBM Plex Sans\',system-ui,sans-serif">'
       '<a href="./">&larr; ARGUS overview</a></nav>\n')
LABEL_ORDER = ['re-check', 'verify', 'design', 'test-print', 'research', 'software', 'change-request']


def page(html):
    # full document for github pages plus a link back to the overview
    if not html.lstrip().lower().startswith('<!doctype'):
        html = HEAD + html
    return html.replace('<div class="wrap">', NAV + '<div class="wrap">', 1)


def gh_json(path):
    try:
        r = subprocess.run(['gh', 'api', path], capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or 'null')
    except Exception:
        return None
    return d if isinstance(d, list) else None


def tasks():
    out = []
    for i in gh_json(f'repos/{REPO_NAME}/issues?state=open&per_page=100') or []:
        if 'pull_request' in i:
            continue
        labs = [l['name'] for l in i['labels']]
        if 'status' in labs:
            continue
        kind = next((k for k in LABEL_ORDER if k in labs), 'other')
        out.append(dict(n=i['number'], title=i['title'], kind=kind, waiting='waiting' in labs, fable='fable' in labs,
                        who=[a['login'] for a in i['assignees']]))
    return out


def commits(n=8):
    r = subprocess.run(['git', 'log', f'-n{n}', '--format=%h%x09%cI%x09%s'], cwd=ROOT, capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        sha, date, subj = line.split('\t', 2)
        out.append(dict(sha=sha, date=date[:10], subject=subj))
    return out


def checks():
    p = BUILD / 'checks.json'
    if not p.exists():
        return None
    items = json.loads(p.read_text())['items']
    cnt = {s: sum(1 for i in items if i['status'] == s) for s in ('PASS', 'WARN', 'FAIL')}
    cnt['PASS'] += sum(1 for i in items if i['status'] not in ('PASS', 'WARN', 'FAIL'))
    bad = [dict(part=i['part'], title=i['title'], status=i['status'], value=str(i.get('value', '')), detail=i.get('detail', ''))
           for i in items if i['status'] in ('WARN', 'FAIL')]
    return dict(count=cnt, issues=sorted(bad, key=lambda x: x['status'] != 'FAIL'))


def main():
    v = V.data()
    rows = BOM.rows()
    spent = round(sum(r['total'] for r in rows), 2)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    sha = os.environ.get('GITHUB_SHA') or subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
                                                         text=True).stdout.strip()
    d = dict(updated=now.strftime('%d %b %Y, %H:%M'), sha=sha[:7], repo=REPO, version=P['version'], spec=SPEC_VERSION,
             board=v['board'], budget=BOM.BUDGET_TL, spent=spent, checks=checks(), tasks=tasks(), commits=commits(),
             facts=[dict(key=f['key'], status=f['status'], verified=f['verified'], parts=len(f['parts']), issue=f['issue'],
                         buy=f['buy_state'], how=f['how']) for f in v['facts']],
             parts=[dict(key=p['key'], name=p['name'], module=p['module'], state=p['state'], unverified=p['unverified'],
                         design=p['design'], recheck=p['recheck']) for p in v['parts']],
             shop=[dict(key=s['key'], buy=s['buy']) for s in v['shop']], buy_txt=v['buy_txt'],
             pages=[f for f, src in PAGES if (BUILD / src).exists()])
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    V.write(v)
    for name, src in PAGES:
        if (BUILD / src).exists():
            (SITE / name).write_text(page((BUILD / src).read_text(encoding='utf-8')), encoding='utf-8')
    tpl = (ROOT / 'tools' / 'pages' / 'site_template.html').read_text(encoding='utf-8')
    (SITE / 'index.html').write_text(page(tpl.replace('/*__DATA__*/null', json.dumps(d, ensure_ascii=False))),
                                     encoding='utf-8')
    (SITE / '.nojekyll').write_text('')
    print('wrote site/ with', ', '.join(sorted(p.name for p in SITE.iterdir() if p.suffix == '.html')))


if __name__ == '__main__':
    main()
