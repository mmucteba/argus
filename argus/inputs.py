# how sure we are about the inputs of a part
#   provisional  it uses a fact that is only assumed or from a shop listing
#   re-check     every input is verified but the part was not re-checked against these exact values
#   confirmed    someone re-checked the part against the current verified values (hash in contracts.yaml)
import hashlib
import json
from argus.spec import FACTS, VERIFIED, CONTRACTS


def inputs_of(rec):
    # traced fact keys plus whole items listed in the contract under depends_on
    keys = set(rec.get('facts') or [])
    for item in (CONTRACTS.get(rec.get('key'), {}) or {}).get('depends_on', []) or []:
        keys.add(f'{item}.*')
    return sorted(keys)


def _value(key):
    item, k = key.split('.', 1)
    v = FACTS[item]['values']
    return v if k == '*' else v[k]


def unverified(keys):
    return sorted({k.split('.')[0] for k in keys if FACTS[k.split('.')[0]]['status'] not in VERIFIED})


def inputs_hash(keys):
    data = [(k, _value(k), FACTS[k.split('.')[0]]['status']) for k in sorted(keys)]
    return hashlib.sha1(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:10]


def state(key, keys):
    un = unverified(keys)
    if un:
        return 'provisional', un
    if (CONTRACTS.get(key) or {}).get('confirmed_inputs') == inputs_hash(keys):
        return 'confirmed', []
    return 're-check', []
