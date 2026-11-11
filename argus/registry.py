# collects every part of the machine
# printed parts: parts/<module>/<key>.py with META and build()
# bought parts: parts/<module>/bought.py with add_bought(add)
import importlib
import sys
from argus import spec as _spec
from argus.spec import META, ROOT, trace

MODULES = ['base', 'light', 'x_axis', 'y_axis', 'slide', 'column', 'optics', 'overview', 'electronics']
NOT_PARTS = {'bought', 'layout', '__init__'}
PARTS = []


def add(name, shape, group, layer, cat, sub, step, color, mass=None, buy=None, note='', density=None,
        orient='zmin', hw=None, holes=None, key=None, module=None, facts=None):
    if facts is None and _spec._TRACE:
        # bought part: the facts read since the previous add belong to this part
        facts = sorted(_spec._TRACE[-1])
        _spec._TRACE[-1].clear()
    PARTS.append(dict(name=name, shape=shape, group=group, layer=layer, cat=cat, sub=sub, step=step,
                      color=META['colors'].get(color, color), mass=mass, buy=buy, note=note, density=density,
                      orient=orient, hw=hw or {}, holes=holes or [], key=key, module=module, facts=facts or []))


def printed_keys(module=None):
    out = []
    for m in ([module] if module else MODULES):
        for f in sorted((ROOT / 'parts' / m).glob('*.py')):
            if f.stem not in NOT_PARTS:
                out.append((m, f.stem))
    return out


def find_module(key):
    for m, k in printed_keys():
        if k == key:
            return m
    raise KeyError(f'no printed part called {key}; see parts/<module>/<key>.py')


def _fresh(name):
    # re-import so numbers read at import time are traced again for every part
    for n in (name, name.rsplit('.', 1)[0] + '.layout'):
        sys.modules.pop(n, None)
    return importlib.import_module(name)


def build_printed(module, key):
    with trace() as facts:
        mod = _fresh(f'parts.{module}.{key}')
        out = mod.build()
    shape, holes = out if isinstance(out, tuple) else (out, [])
    meta = dict(mod.META)
    rec = dict(shape=shape, cat='printed', holes=holes, key=key, module=module, **meta)
    rec['facts'] = sorted(facts)
    return rec


def build(only=None):
    # only = a printed part key to build just that part, else the whole machine
    PARTS.clear()
    if only:
        add(**build_printed(find_module(only), only))
        return PARTS
    for m in MODULES:
        for _, k in printed_keys(m):
            add(**build_printed(m, k))
        n0 = len(PARTS)
        _spec._TRACE.append(set())
        try:
            _fresh(f'parts.{m}.bought').add_bought(add)
        finally:
            _spec._TRACE.pop()
        for p in PARTS[n0:]:
            p['module'] = m
    return PARTS
