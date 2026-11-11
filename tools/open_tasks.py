# opens a github issue for every tasks/*.md that does not have one yet (matched by title)
# runs in github actions with GH_TOKEN; locally it needs the gh cli logged in
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
COLORS = {'design': '5a3ea6', 'fable': 'c62f2f', 'software': '1b78a3', 'change-request': 'd47108', 'waiting': 'bfbfbf',
          'research': '2f7d4f', 'test-print': 'd9c062'}


def gh(*args, **kw):
    return subprocess.run(['gh', *args], capture_output=True, text=True, **kw)


def parse(path):
    txt = path.read_text(encoding='utf-8')
    head, body = {}, txt
    if txt.startswith('---\n'):
        end = txt.index('\n---\n', 4)
        for line in txt[4:end].splitlines():
            k, _, v = line.partition(':')
            head[k.strip()] = v.strip().strip('"')
        body = txt[end + 5:]
    return head, body


def main():
    have = {i['title'] for i in json.loads(gh('issue', 'list', '--state', 'all', '--limit', '500', '--json', 'title').stdout or '[]')}
    for name, color in COLORS.items():
        gh('label', 'create', name, '--color', color, '--force')
    made = 0
    for f in sorted((ROOT / 'tasks').glob('*.md')):
        if f.name == 'README.md':
            continue
        head, body = parse(f)
        title = head.get('title') or f.stem
        if title in have:
            continue
        intro = []
        if head.get('part'):
            intro.append(f"**Part:** `{head['part']}`")
        if head.get('who'):
            intro.append(f"**Best done by:** {head['who']}")
        intro.append(f'**Prompt file:** `tasks/{f.name}`. Assign yourself before you start; guide in REHBER.md.')
        full = '  \n'.join(intro) + '\n\n---\n\n' + body
        tmp = ROOT / 'build' / f'issue_{f.stem}.md'
        tmp.parent.mkdir(exist_ok=True)
        tmp.write_text(full, encoding='utf-8')
        args = ['issue', 'create', '--title', title, '--body-file', str(tmp)]
        for lab in [x.strip() for x in head.get('labels', '').split(',') if x.strip()]:
            args += ['--label', lab]
        r = gh(*args)
        print(title, '->', (r.stdout or r.stderr).strip())
        made += r.returncode == 0
    print(made, 'issue(s) opened')


if __name__ == '__main__':
    sys.exit(main())
