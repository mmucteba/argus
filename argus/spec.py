# loads spec/*.yaml into P (parameters), IF (interfaces), META (names and texts)
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / 'spec'


def _load(name):
    return yaml.safe_load((SPEC_DIR / name).read_text(encoding='utf-8'))


_raw = _load('params.yaml')
SPEC_VERSION = _raw.pop('spec_version')
P = {k: (tuple(v) if isinstance(v, list) else v) for k, v in _raw.items()}
P['version'] = P.pop('model_version')

# derived heights along the optical axis
P['z_slide_bot'] = P['holder_z'][1] - 1.2
P['z_focal'] = P['z_slide_bot'] + P['slide_t']
P['z_cover_top'] = P['z_focal'] + P['cover_t']
P['z_obj_tip'] = P['z_cover_top'] + P['wd']          # zoom lens front
P['z_shoulder'] = P['z_obj_tip']
P['z_cmount'] = P['z_obj_tip'] + P['lens_len'] - P['lens_thread']
P['z_sensor'] = P['z_cmount'] + 17.526               # c mount flange focal distance

def _num(v):
    # a number or a formula of parameter names, like "xblk_l - 14"
    if isinstance(v, str):
        return float(eval(v, {'__builtins__': {}}, dict(P)))
    return float(v)


IF = _load('interfaces.yaml')
for _name, _f in IF.items():
    _f['pattern'] = [[_num(a) for a in pt] for pt in _f['pattern']]
    if 'd' in _f:
        _f['d'] = _num(_f['d'])
    for _part, _h in _f['holes'].items():
        for _k in ('plane', 'depth', 'd'):
            if _k in _h:
                _h[_k] = _num(_h[_k])
META = _load('meta.yaml')
CONTRACTS = _load('contracts.yaml') if (SPEC_DIR / 'contracts.yaml').exists() else {}


def pat(name, only=None):
    # hole centres of an interface as tuples, optionally a subset by index
    pts = [tuple(p) for p in IF[name]['pattern']]
    return [pts[i] for i in only] if only is not None else pts
