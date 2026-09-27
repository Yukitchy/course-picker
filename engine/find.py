#!/usr/bin/env python3
"""モデルコースを探す。 python3 engine/find.py [語 ...] [--pack yuuki]
語は name/tag/chips/why/行程/経由地/エリア/ゲスト/ジャンル(例: 雨の日OK)に AND で部分一致。語なしで全件。"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
a = sys.argv[1:]; pack = 'yuuki'
if '--pack' in a: i = a.index('--pack'); pack = a[i + 1]; del a[i:i + 2]
rows = json.load(open(ROOT / 'packs' / pack / 'courses.json'))
def blob(r):
    c = r.get('course', {})
    return json.dumps([c.get(k) for k in ('name', 'tag', 'chips', 'why', 'steps', 'stops', 'food')] + [r.get('area'), r.get('guest'), r.get('genres')], ensure_ascii=False).lower()
hits = [r for r in rows if all(w.lower() in blob(r) for w in a)]
for r in hits:
    c = r.get('course', {})
    stops = ' → '.join(c.get('stops', [])[:6])
    print(f"{r['key']:<26} {c.get('name') or '(page only)'} — {c.get('tag', '')}\n{'':<26} [{'/'.join(r.get('genres', []))}] {r.get('area')} · {r.get('guest')} · {r.get('date')} · {r.get('status')}\n{'':<26} {stops}\n{'':<26} {r['url']}#detail-{c.get('id', '')}\n")
print(f'{len(hits)} / {len(rows)} courses')
