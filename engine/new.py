#!/usr/bin/env python3
"""選んだモデルコースから新しい選択ページのたたき台を作る。
python3 engine/new.py <出力フォルダ> <key> [<key> ...] [--pack yuuki]
例: python3 engine/new.py ~/lisa-tokyo-day patrick-tokyo-day:A rick-tokyo-oct5:F manga-week:3
コースは並べた順に A,B,C… に振り直す。page.json の TODO を埋めて python3 build.py。"""
import datetime, json, os, pathlib, re, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
a = sys.argv[1:]; pack = 'yuuki'; req = None
if '--pack' in a: i = a.index('--pack'); pack = a[i + 1]; del a[i:i + 2]
if '--from-issue' in a:  # 一覧ページのフォーム→GitHub issue→Actions から呼ばれる
    i = a.index('--from-issue'); req = json.load(open(a[i + 1])); del a[i:i + 2]
    slug = re.sub(r'[^a-z0-9-]+', '-', str(req.get('slug', '')).lower()).strip('-')[:60] or 'plan'
    out = ROOT / 'plans' / slug; n = 2
    while out.exists(): out = ROOT / 'plans' / f'{slug}-{n}'; n += 1
    keys = [str(k) for k in req.get('keys', [])][:6]
    if not keys: sys.exit('コースが選ばれていません')
else:
    if len(a) < 2: sys.exit(__doc__)
    out = pathlib.Path(os.path.expanduser(a[0])); keys = a[1:]
rows = {r['key']: r for r in json.load(open(ROOT / 'packs' / pack / 'courses.json'))}
miss = [k for k in keys if k not in rows or rows[k].get('page_only')]
if miss: sys.exit(f'見つからない/中身なし: {miss}  (find.py で key を確認)')
if out.exists() and any(out.iterdir()): sys.exit(f'{out} は空ではありません')
out.mkdir(parents=True, exist_ok=True)
courses, ph = [], {}
for n, k in enumerate(keys):
    cid = chr(65 + n); c = dict(rows[k]['course']); c['id'] = cid; c['from'] = k
    c['chips'] = [x for x in c.get('chips', []) if not re.search(r'[$¥€£]|\d+\s*(円|yen|usd)', x, re.I)]
    courses.append(c); ph[cid] = rows[k].get('photos') or {}
page = {'title': 'TODO: Tokyo, <day>: courses for <guest>', 'kicker': 'TODO: Tokyo · <Weekday>, <Month> <d>',
        'h1': 'TODO: short headline, <span class="nb">second half.</span>', 'lead': 'TODO: one sentence about the day.',
        'facts': [['Guide', 'Yuuki'], ['Time', 'TODO'], ['Start', 'TODO']], 'subject': 'TODO: <Mon d> tour: I choose',
        'meet_sub': 'TODO', 'meet_text': 'TODO', 'meet_hint': 'TODO', 'meet_place': 'TODO: Google Maps query',
        'footer': 'Reply to Yuuki with the letter of the course you want. Times are approximate and can move on the day.'}
if req:
    try: d = datetime.date.fromisoformat(req.get('date', ''))
    except ValueError: d = None
    day = f"{d:%A}, {d:%B} {d.day}" if d else 'TODO: day'
    area = (rows[keys[0]].get('area') or 'Tokyo').split(' / ')[0]
    guest, meet = req.get('guest') or 'TODO', req.get('meet') or 'TODO: meeting place'
    start, end = req.get('start') or '10:00', req.get('end') or '15:00'
    page.update({'title': f'{area}, {day}: {len(keys)} courses for {guest}', 'kicker': f'{area} · {day}',
        'h1': 'Your day, <span class="nb">your pick.</span>',
        'lead': f'{len(keys)} ways to spend the day. Tap one to see the plan, the route and where we eat.',
        'facts': [['Guide', 'Yuuki'], ['Time', f'{start} to about {end}'], ['Start', meet]],
        'subject': (f'{d:%b} {d.day} tour: I choose' if d else 'Tour: I choose'),
        'meet_sub': f'{meet} at {start}.', 'meet_text': f'We meet at {meet}.',
        'meet_hint': 'If another place or time is easier, tell me and I will change it.', 'meet_place': meet})
    json.dump(req, open(out / 'request.json', 'w'), ensure_ascii=False, indent=1)
    if os.environ.get('GITHUB_OUTPUT'):
        open(os.environ['GITHUB_OUTPUT'], 'a').write(f'dir={out.relative_to(ROOT)}\n')
json.dump(courses, open(out / 'courses.json', 'w'), ensure_ascii=False, indent=1)
json.dump(ph, open(out / 'photos.json', 'w'), ensure_ascii=False, indent=1)
json.dump(page, open(out / 'page.json', 'w'), ensure_ascii=False, indent=1)
shutil.copy(ROOT / 'engine' / 'template_build.py', out / 'build.py')
shutil.copy(ROOT / 'engine' / 'devbar.js', out / 'devbar.js')
subprocess.run([sys.executable, 'build.py'], cwd=out, check=True)
nop=[c['from'] for c in courses if not (ph[c['id']].get('card') or {}).get('thumb')]
if nop: print('  ⚠️ 写真なし(photos.jsonに要追加):', ', '.join(nop))
print(f'OK {out}\n  コース: ' + ', '.join(f"{c['id']}={c['from']}" for c in courses))
print('  次: page.json の TODO と courses.json の時刻・集合場所を今回用に直す → 営業日を公式で再確認 → python3 build.py')
