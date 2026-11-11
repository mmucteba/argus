# bill of materials from spec/bom.yaml
from argus.spec import _load

_B = _load('bom.yaml')
BUDGET_TL = _B['budget_tl']
STATUS_TXT = _B['status_txt']
HARDWARE = [(h['item'], h['qty']) for h in _B['hardware']]
REDESIGN = _B['redesign']
PART_KEY = _B['part_key']
FREE_SHIPPING = _B['free_shipping_tl']


def rows():
    return [dict(key=i['key'], step=i['step'], store=i['store'], item=i['item'], url=i['url'], unit=i['unit_tl'],
                 qty=i['qty'], total=round(i['unit_tl'] * i['qty'], 2), status=i['status'], note=i['note'])
            for i in _B['items']]


SEARCH = ('arama?q=', '/ara?q=', 'search?q=')
BUY_TXT = {'picked': 'picked, product link', 'home': 'we make it', 'no-link': 'picked, no product link', 'open': 'not picked yet'}


def buy_state(r):
    # picked one product page, home we make it, no-link picked but only a search or nothing, open not decided yet
    if r['status'] == 'later' or r['store'] in ('tbd', ''):
        return 'open'
    if r['store'] == 'home':
        return 'home'
    if not r['url'] or any(s in r['url'] for s in SEARCH):
        return 'no-link'
    return 'picked'


def by_key():
    return {r['key']: dict(r, buy=buy_state(r)) for r in rows()}


def fact_buy(fact):
    # bought rows behind a fact and the weakest buy state among them
    keys = fact.get('buy') or []
    rs = [by_key()[k] for k in keys]
    rank = ['open', 'no-link', 'home', 'picked']
    worst = min((r['buy'] for r in rs), key=rank.index) if rs else None
    return rs, worst
