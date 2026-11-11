# loads spec/*.yaml: F facts, P parameters, IF interfaces, META texts, CONTRACTS
# every read of a fact, a parameter or an interface is traced, so the checks know which facts each part depends on
# params and interfaces may be formulas of facts and earlier params, like "lens.d / 2" or "xblk_l - 14"
import contextlib
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / 'spec'
VERIFIED = ('datasheet', 'standard', 'measured')
_TRACE = []


def _load(name):
    p = SPEC_DIR / name
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.exists() else {}


def _note(keys):
    if _TRACE:
        _TRACE[-1].update(keys)


@contextlib.contextmanager
def trace():
    # collects the fact keys (item.value) read inside the block
    s = set()
    _TRACE.append(s)
    try:
        yield s
    finally:
        _TRACE.pop()
        _note(s)


class _Item:
    def __init__(self, name, values):
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_values', values)

    def __getattr__(self, k):
        vals = object.__getattribute__(self, '_values')
        name = object.__getattribute__(self, '_name')
        if k not in vals:
            raise AttributeError(f'fact {name} has no value {k}; see spec/facts.yaml')
        _note({f'{name}.{k}'})
        return vals[k]


class _Facts:
    def __init__(self, raw):
        object.__setattr__(self, '_items', {k: _Item(k, v['values']) for k, v in raw.items()})

    def __getattr__(self, k):
        items = object.__getattribute__(self, '_items')
        if k not in items:
            raise AttributeError(f'no fact item {k}; see spec/facts.yaml')
        return items[k]


FACTS = _load('facts.yaml')
F = _Facts(FACTS)
PARAM_DEPS = {}


class _Params(dict):
    def __getitem__(self, k):
        _note(PARAM_DEPS.get(k, ()))
        return dict.__getitem__(self, k)


P = _Params()


class _NS(dict):
    # namespace for formulas: fact items and parameters, reads are traced
    def __getitem__(self, k):
        if k in FACTS:
            return getattr(F, k)
        if k in P:
            return P[k]
        if k in ('min', 'max', 'abs', 'round'):
            return {'min': min, 'max': max, 'abs': abs, 'round': round}[k]
        raise KeyError(f'{k} is neither a fact item nor a parameter')


def _eval(v):
    # a number, a list, or a formula string; returns (value, fact keys it depends on)
    with trace() as deps:
        if isinstance(v, str):
            out = eval(v, {'__builtins__': {}}, _NS())
        elif isinstance(v, list):
            out = [_eval(x)[0] for x in v]
        else:
            out = v
    if isinstance(out, list):
        out = tuple(out)
    return out, deps


_raw = _load('params.yaml')
SPEC_VERSION = _raw.pop('spec_version')
_raw['version'] = _raw.pop('model_version')
_raw.update({  # derived heights along the optical axis
    'z_slide_bot': 'holder_z[1] - 1.2',
    'z_focal': 'z_slide_bot + slide_t',
    'z_cover_top': 'z_focal + cover_t',
    'z_obj_tip': 'z_cover_top + wd',                   # zoom lens front
    'z_shoulder': 'z_obj_tip',
    'z_cmount': 'z_obj_tip + lens_len - lens_thread',
    'z_sensor': 'z_cmount + hq_camera.flange_focal',   # c mount flange focal distance
})
for _k, _v in _raw.items():
    if _k == 'version' or isinstance(_v, dict):
        dict.__setitem__(P, _k, _v)
        PARAM_DEPS[_k] = set()
        continue
    _val, _deps = _eval(_v)
    dict.__setitem__(P, _k, _val)
    PARAM_DEPS[_k] = _deps

IF_DEPS = {}       # every fact an interface uses, holes included
IF_PAT_DEPS = {}   # facts behind the hole centres only, what a part's geometry really reads


class _Interfaces(dict):
    def __getitem__(self, k):
        _note(IF_DEPS.get(k, ()))
        return dict.__getitem__(self, k)


IF = _Interfaces()
for _name, _f in _load('interfaces.yaml').items():
    with trace() as _deps:
        with trace() as _pdeps:
            _f['pattern'] = [[float(_eval(a)[0]) for a in pt] for pt in _f['pattern']]
        if 'd' in _f:
            _f['d'] = float(_eval(_f['d'])[0])
        for _part, _h in _f['holes'].items():
            for _k in ('plane', 'depth', 'd'):
                if _k in _h:
                    _h[_k] = float(_eval(_h[_k])[0])
    dict.__setitem__(IF, _name, _f)
    IF_DEPS[_name] = _deps
    IF_PAT_DEPS[_name] = _pdeps

META = _load('meta.yaml')
CONTRACTS = _load('contracts.yaml')


def pat(name, only=None):
    # hole centres of an interface as tuples, optionally a subset by index
    _note(IF_PAT_DEPS[name])
    pts = [tuple(p) for p in dict.__getitem__(IF, name)['pattern']]
    return [pts[i] for i in only] if only is not None else pts


def fact_status(key):
    # key like "lens.d" or "lens"
    return FACTS[key.split('.')[0]]['status']


def is_verified(key):
    return fact_status(key) in VERIFIED
