#!/usr/bin/env python3
"""各ページの build.py を書き込み無しで実行し、コースを1つの台帳に吸い上げる。
python3 engine/extract.py [pack]  -> packs/<pack>/courses.json"""
import builtins, io, json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACK = ROOT / 'packs' / (sys.argv[1] if len(sys.argv) > 1 else 'yuuki')
KEEP = ('id', 'name', 'tag', 'chips', 'why', 'steps', 'stops', 'moves', 'food', 'good', 'mind', 'links', 'title', 'date', 'day')

def safe_open(f, mode='r', *a, **k):
    if any(c in mode for c in 'wax'):
        return io.StringIO() if 'b' not in mode else io.BytesIO()
    return builtins.open(f, mode, *a, **k)

def load(repo):
    src = (repo / 'build.py').read_text()
    ns = {'__name__': 'extract', 'open': safe_open}
    cwd = os.getcwd(); os.chdir(repo)
    try:
        sys.stdout, out = io.StringIO(), sys.stdout
        try: exec(compile(src, str(repo / 'build.py'), 'exec'), ns)
        finally: sys.stdout = out
    finally: os.chdir(cwd)
    items = ns.get('COURSES') or ns.get('DAYS') or ([ns['DAY']] if isinstance(ns.get('DAY'), dict) else [])
    return items, ns.get('PH', {})

def plain(v):
    return json.loads(json.dumps(v, ensure_ascii=False, default=str))

rows = []
for s in json.load(open(PACK / 'sources.json')):
    repo = pathlib.Path(os.path.expanduser(s['repo']))
    base = {k: s.get(k, '') for k in ('url', 'guest', 'date', 'area', 'status')}
    base['page'] = repo.name
    base['note'] = s.get('note', '')
    if s.get('page_only') or not (repo / 'build.py').exists():
        rows.append({**base, 'key': repo.name, 'page_only': True}); continue
    try:
        items, ph = load(repo)
    except Exception as e:
        print('!!', repo.name, e); rows.append({**base, 'key': repo.name, 'page_only': True, 'error': str(e)}); continue
    for i, c in enumerate(items):
        cid = str(c.get('id', i + 1))
        r = {**base, 'key': f'{repo.name}:{cid}', 'course': {k: plain(c[k]) for k in KEEP if k in c}}
        r['course'].setdefault('name', s.get('name') or repo.name)
        p = ph.get(cid) if isinstance(ph, dict) else None
        if isinstance(p, dict): r['photos'] = plain(p)
        rows.append(r)
    print(f'{repo.name}: {len(items)}')
GEN = json.load(open(PACK / 'genres.json')) if (PACK / 'genres.json').exists() else {}
for r in rows:
    c = r.get('course') or {}
    stops = [x for x in c.get('stops', []) if 'hotel' not in x.lower()]
    base = json.dumps([c.get('name'), c.get('tag'), c.get('chips'), stops], ensure_ascii=False).lower()
    food = base + json.dumps([f[0] for f in c.get('food', []) if f], ensure_ascii=False).lower()
    def hit(k, b):
        return re.search(r'\b' + re.escape(k.lower()) + r'\b', b) if k.isascii() else k.lower() in b
    r['genres'] = [g for g, kws in GEN.items() if any(hit(k, food if g == '食べ歩き・グルメ' else base) for k in kws)]
json.dump(rows, open(PACK / 'courses.json', 'w'), ensure_ascii=False, indent=1)
print('->', PACK / 'courses.json', len(rows))
