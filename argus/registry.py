# collects every part of the machine
# printed parts: parts/<module>/<key>.py with META and build()
# bought parts: parts/<module>/bought.py with add_bought(add)
import importlib
from argus.spec import META, ROOT

MODULES = ['base', 'light', 'x_axis', 'y_axis', 'slide', 'column', 'optics', 'overview', 'electronics']
NOT_PARTS = {'bought', 'layout', '__init__'}
PARTS = []


def add(name, shape, group, layer, cat, sub, step, color, mass=None, buy=None, note='', density=None,
        orient='zmin', hw=None, holes=None, key=None, module=None):
    PARTS.append(dict(name=name, shape=shape, group=group, layer=layer, cat=cat, sub=sub, step=step,
                      color=META['colors'].get(color, color), mass=mass, buy=buy, note=note, density=density,
                      orient=orient, hw=hw or {}, holes=holes or [], key=key, module=module))


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


def build_printed(module, key):
    mod = importlib.import_module(f'parts.{module}.{key}')
    out = mod.build()
    shape, holes = out if isinstance(out, tuple) else (out, [])
    meta = dict(mod.META)
    return dict(shape=shape, cat='printed', holes=holes, key=key, module=module, **meta)


def build(only=None):
    # only = a printed part key to build just that part, else the whole machine
    PARTS.clear()
    if only:
        add(**build_printed(find_module(only), only))
        return PARTS
    for m in MODULES:
        for _, k in printed_keys(m):
            add(**build_printed(m, k))
        importlib.import_module(f'parts.{m}.bought').add_bought(add)
    return PARTS
