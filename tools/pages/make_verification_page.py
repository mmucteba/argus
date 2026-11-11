# builds the verification map from facts, parts, the bill of materials and the open issues into build/argus-verification.html
#   python tools/pages/make_verification_page.py
import json, pathlib, re, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import audit
from argus.spec import FACTS, VERIFIED
from argus import bom as BOM

REPO = 'https://github.com/mmucteba/argus'
OUT = ROOT / 'build' / 'argus-verification.html'

# what to do to verify each fact, one line
HOW = {
    'printer_fit': 'Print the fit coupons, then note which hole fits each real part',
    'm3_insert': 'Pick the insert type, then read the outer diameter and length off the package',
    't8_nut': 'Maker drawing, or measure the flange and holes when the nut arrives',
    'endstop_board': 'Measure the board: hole spacing, fork gap and height',
    'lens': 'Waveshare drawing; measure the barrel and the best-focus height when it arrives',
    'led_ring': 'Datasheet, or measure outer and inner diameter and thickness',
    'led_card': 'Measure the card: size, LED position, holes',
    'heatsink': 'Measure it when it arrives',
    'diffuser': 'Decide the material and thickness, then measure the disc',
    'overview_camera': 'Pick the camera first, then use its board drawing',
    'power_parts': 'Pick the shifter, fuse holder and Wago, then measure every power part',
    'rod_8mm': 'Caliper on one rod',
    't8_screw': 'Check 8 mm of travel per turn and the 8 mm diameter',
    'coupling': 'Measure the outer diameter and length',
    'printer': "Write down the team printer's real build volume",
}

# short names for the map
SHORT = {
    'rod': '8 mm rods', 'LM8UU': 'LM8UU 10-pack', 'LM8UU_sp': 'LM8UU spares', 'T8 screw': 'T8 lead screw',
    'T8 nut': 'T8 spring nut', '608': '608ZZ bearing', 'endstop': 'optical endstop', 'BYJ': '28BYJ-48',
    'hw': 'screws, inserts', 'HQ': 'HQ camera', 'lens': 'zoom lens', 'ring': 'LED ring', 'LED': '3 W LED card',
    'heatsink': 'heatsink', 'diffuser': 'diffuser', 'slide': 'glass slides', 'Uno': 'Arduino Uno', 'Pi': 'Pi 3B+',
    'ovcam': 'overview camera', 'dcjack': 'DC jack', 'switch': 'rocker switch', 'buck': 'LM2596 buck',
    'wago': 'Wago clamps', 'shifter': '74HCT125', 'fuse': 'fuse holder', 'coupling': 'couplings', 'NEMA17': 'NEMA17',
    'A4988': 'A4988', 'A4988 hs': 'A4988 heatsink', 'shield': 'CNC shield', 'drv': 'DRV8825', 'jumper': 'jumper wires',
    'camcable': 'camera cable', 'led5': '5 mm LEDs', 'adapter': '12 V adapter', 'psu': 'Pi supply', 'sd': 'microSD',
    'wiring': 'wire', 'eth': 'Ethernet cable', 'piheat': 'Pi heatsinks', 'thermal': 'thermal tape', 'base': 'plywood base',
    'pla': 'PLA filament', 'feet': 'rubber feet',
}


def issues():
    # open issue numbers by kind and key, empty when gh is missing
    try:
        r = subprocess.run(['gh', 'api', 'repos/mmucteba/argus/issues?state=open&per_page=100'],
                           capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout or '[]')
    except Exception:
        return {}
    out = {}
    for i in d if isinstance(d, list) else []:
        m = re.match(r'\[([\w-]+)\] (\w+)', i['title'])
        if m:
            out[(m.group(1), m.group(2))] = i['number']
        if i['title'] == 'Status board':
            out[('board', '')] = i['number']
    return out


def data():
    rows, used, bought = audit.collect()
    iss = issues()
    shop = BOM.by_key()
    facts = []
    for k, f in FACTS.items():
        rs, worst = BOM.fact_buy(f)
        facts.append(dict(key=k, item=f['item'], status=f['status'], evidence=str(f.get('evidence', '')), values=f['values'],
                          verified=f['status'] in VERIFIED, parts=sorted(used.get(k, ())), bought=sorted(bought.get(k, ())),
                          buy=[r['key'] for r in rs], buy_state=worst, how=HOW.get(k, ''), issue=iss.get(('verify', k))))
    parts = []
    for k, r in rows.items():
        fs = {}
        for key in r['keys']:
            i, v = key.split('.', 1)
            fs.setdefault(i, []).append(v)
        parts.append(dict(key=k, name=r['name'], module=r['module'], state=r['state'], unverified=r['unverified'], facts=fs,
                          recheck=iss.get(('re-check', k)), design=iss.get(('design', k))))
    items = []
    for key, r in shop.items():
        items.append(dict(key=key, short=SHORT.get(key, key), item=r['item'], store=r['store'], url=r['url'] or '',
                          unit=r['unit'], qty=r['qty'], total=r['total'], status=r['status'],
                          status_txt=BOM.STATUS_TXT.get(r['status'], r['status']), buy=r['buy'], note=r['note'] or '',
                          facts=[f['key'] for f in facts if key in f['buy']]))
    return dict(facts=facts, parts=parts, shop=items, hardware=BOM.HARDWARE, buy_txt=BOM.BUY_TXT, repo=REPO,
                board=iss.get(('board', '')), coupon=iss.get(('test-print', 'fit')), date=time.strftime('%d %b %Y'))


def write(d):
    tpl = (ROOT / 'tools' / 'pages' / 'verification_template.html').read_text(encoding='utf-8')
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(tpl.replace('/*__DATA__*/null', json.dumps(d, ensure_ascii=False)), encoding='utf-8')
    print('wrote', OUT.relative_to(ROOT))


def main():
    write(data())


if __name__ == '__main__':
    main()
