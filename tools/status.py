# prints every printed part with its status and open question, from spec/contracts.yaml
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from argus.spec import CONTRACTS, SPEC_VERSION

print(f'spec version {SPEC_VERSION}\n')
for k, c in sorted(CONTRACTS.items(), key=lambda kv: (kv[1]['status'] == 'ok', kv[1]['module'], kv[0])):
    flag = '' if c['built_for_spec'] == SPEC_VERSION else f'  (built for spec {c["built_for_spec"]})'
    print(f"{c['status']:<18} {c['module']:<12} {k:<22}{flag}")
    if c.get('open'):
        print(f"{'':<31}{c['open']}")
