#!/usr/bin/env python3
"""台帳からモデルコース一覧ページを作る。 python3 engine/catalog.py [pack] -> index.html"""
import html, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
pack = sys.argv[1] if len(sys.argv) > 1 else 'yuuki'
rows = json.load(open(ROOT / 'packs' / pack / 'courses.json'))
import collections, re
PRICE = re.compile(r'[$¥€£]|\d+\s*(円|yen|usd)', re.I)
GC = collections.Counter(g for r in rows for g in r.get('genres', []))
AC = collections.Counter(g for r in rows for g in r.get('areas', []))
PLANS = []
for d in sorted((ROOT / 'plans').glob('*/page.json'), reverse=True):
    PLANS.append((d.parent.name, json.load(open(d)).get('title', d.parent.name)))
e = lambda s: html.escape(str(s or ''))
ST = {'decided': '決定', 'done': '実施済み', 'proposed': '提案'}

def card(r):
    c = r.get('course'); url = r['url']
    if not c:
        return (f'<a class="cc po" href="{e(url)}" target="_blank" rel="noopener" data-q="{e(r["page"])} {e(r["area"])} {e(r["guest"])}">'
                f'<span class="cb"><span class="meta">{e(r["area"])} · {e(r["guest"])} · {e(r["date"])}</span>'
                f'<strong>{e(r["page"])}</strong><span class="tag">ページのみ（コースデータなし）</span></span></a>')
    img = ((r.get('photos') or {}).get('card') or {}).get('thumb', '')
    st = r.get('status', ''); dec = st.startswith('decided') and (st == 'decided' or st.endswith(':' + str(c.get('id'))))
    badge = ST['decided'] if dec else ST.get(st.split(':')[0], st)
    chips = ''.join(f'<li>{e(x)}</li>' for x in c.get('chips', []) if not PRICE.search(x))
    gl = ''.join(f'<span>{e(g)}</span>' for g in r.get('genres', []))
    stops = ' → '.join(e(x) for x in c.get('stops', [])[1:5])
    q = ' '.join(map(str, [c.get('name'), c.get('tag'), ' '.join(x for x in c.get('chips', []) if not PRICE.search(x)), ' '.join(c.get('stops', [])), r['area'], r['guest'], r['key']]))
    return (f'<article class="cc{" dec" if dec else ""}" data-q="{e(q)}" data-g="{e("|".join(r.get("genres", [])))}" data-a="{e("|".join(r.get("areas", [])))}" data-k="{e(r["key"])}" data-n="{e(c.get("name"))}">'
            + (f'<img src="{e(img)}" alt="" loading="lazy">' if img else '<div class="noimg">No photo</div>')
            + f'<span class="cb"><span class="meta">{e(r["area"])} · {e(r["guest"])} · {e(r.get("note") or r["date"])}<b class="st">{e(badge)}</b></span>'
            f'<strong>{e(c.get("name"))}</strong><span class="tag">{e(c.get("tag"))}</span><span class="gl">{gl}</span><ul class="ch">{chips}</ul>'
            f'<span class="stops">{stops}</span>'
            f'<span class="row"><a href="{e(url)}#detail-{e(c.get("id"))}" target="_blank" rel="noopener">元のページで見る ↗</a>'
            f'<button type="button" class="key" data-k="{e(r["key"])}">{e(r["key"])}</button></span>'
            f'<button type="button" class="pick">＋ このコースを選ぶ</button></span></article>')

n = sum(1 for r in rows if r.get('course')); pages = len({r['page'] for r in rows})
page = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>モデルコース棚</title><link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png"><link rel="icon" type="image/png" sizes="512x512" href="icon-512.png"><link rel="apple-touch-icon" href="apple-touch-icon.png"><meta name="robots" content="noindex,nofollow">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fffdf6;--card:#fff;--ink:#111;--mute:#767065;--line:#eae4d6;--acc:#1a5c3a}}
*{{box-sizing:border-box;min-width:0}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,-apple-system,"Hiragino Sans",sans-serif;line-height:1.6}}
.wrap{{max-width:1120px;margin:0 auto;padding:28px 20px 60px}}
.kicker{{font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--acc);margin:0 0 8px}}
h1{{font-weight:800;font-size:clamp(30px,5vw,46px);line-height:1.08;letter-spacing:-.025em;margin:0 0 10px}}
.lead{{color:var(--mute);margin:0 0 18px;max-width:680px}}
.how{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:0 0 18px;font-size:14px}}
.how b{{display:block;margin-bottom:4px}} .how code{{background:#f3efe4;border-radius:4px;padding:1px 6px;font-size:13px}}
#q{{width:100%;font:inherit;font-size:16px;padding:12px 14px;border:2px solid var(--ink);border-radius:8px;background:#fff;margin:0 0 8px}}
.count{{font-size:13px;color:var(--mute);margin:0 0 16px}}
.genres{{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px}}
.genres button{{font:inherit;font-size:13px;font-weight:600;background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:6px 12px;cursor:pointer}}
.genres button i{{font-style:normal;color:var(--mute);font-weight:400;margin-left:2px}}
.genres button.on{{background:var(--ink);color:#fff;border-color:var(--ink)}} .genres button.on i{{color:#ccc}}
.fl{{font-size:11.5px;font-weight:600;letter-spacing:.1em;color:var(--mute);margin:10px 0 0}}
.ar{{color:var(--mute)}}
.pick{{font:inherit;font-size:13px;font-weight:600;margin-top:10px;background:#fff;border:1.5px dashed var(--acc);color:var(--acc);border-radius:8px;padding:8px;cursor:pointer}}
.cc.sel{{outline:3px solid var(--acc);outline-offset:-3px}} .cc.sel .pick{{background:var(--acc);color:#fff;border-style:solid}}
.bar{{position:fixed;left:0;right:0;bottom:0;background:var(--ink);color:#fff;padding:12px 16px calc(12px + env(safe-area-inset-bottom));display:flex;gap:12px;align-items:center;justify-content:space-between;z-index:5}}
.bar[hidden]{{display:none}} .bar span{{font-size:14px}} .bar button{{font:inherit;font-weight:700;background:#fff;color:var(--ink);border:0;border-radius:8px;padding:10px 16px;cursor:pointer;white-space:nowrap}}
body.has-bar .wrap{{padding-bottom:110px}}
dialog{{border:0;border-radius:12px;padding:0;width:min(520px,calc(100vw - 24px));max-height:calc(100vh - 24px)}} dialog::backdrop{{background:rgba(0,0,0,.45)}}
.dlg{{padding:20px}} .dlg h2{{font-size:20px;margin:0 0 4px}} .dlg ol{{margin:6px 0 14px;padding-left:20px;font-size:14px}}
.dlg label{{display:block;font-size:12.5px;font-weight:600;color:var(--mute);margin:10px 0 4px}}
.dlg input{{width:100%;font:inherit;font-size:16px;padding:9px 11px;border:1px solid var(--line);border-radius:7px}}
.dlg .two{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.dlg .go{{display:block;width:100%;margin-top:16px;font:inherit;font-weight:700;font-size:16px;background:var(--ink);color:#fff;border:0;border-radius:8px;padding:13px;cursor:pointer}}
.dlg .sub{{display:block;width:100%;margin-top:8px;font:inherit;font-size:14px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px;cursor:pointer}}
.dlg .note{{font-size:12.5px;color:var(--mute);margin:10px 0 0}}
.plans{{margin:0 0 18px;padding:0;list-style:none;font-size:14px}} .plans li{{padding:6px 0;border-bottom:1px solid var(--line)}} .plans a{{color:var(--ink)}}
.gl{{display:flex;flex-wrap:wrap;gap:4px}} .gl span{{font-size:11.5px;font-weight:600;color:var(--acc);background:#eef5f0;border-radius:4px;padding:1px 7px}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}
.cc{{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;color:inherit;text-decoration:none}}
.cc.dec{{border:2px solid var(--acc)}} .cc[hidden]{{display:none}}
.cc>img,.noimg{{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;background:#f0ebe0}}
.noimg{{display:flex;align-items:center;justify-content:center;color:var(--mute);font-size:13px}}
.cb{{display:flex;flex-direction:column;gap:4px;padding:14px 16px 16px;flex:1}}
.meta{{font-size:12px;color:var(--mute);display:flex;flex-wrap:wrap;gap:0 6px;align-items:center}}
.st{{margin-left:auto;font-size:11px;font-weight:600;color:var(--acc);border:1px solid var(--acc);border-radius:4px;padding:0 6px}}
.cc strong{{font-weight:800;font-size:20px;line-height:1.2;letter-spacing:-.02em}}
.tag{{font-size:14px;color:var(--mute)}}
.ch{{list-style:none;margin:2px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:5px}}
.ch li{{font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;border:1px solid var(--line);border-radius:4px;padding:1px 7px;color:var(--mute)}}
.stops{{font-size:12.5px;color:var(--mute);margin-top:2px}}
.row{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;margin-top:auto;padding-top:10px}}
.row a{{font-size:13px;color:var(--ink);text-decoration:underline;text-underline-offset:3px}}
.key{{font:inherit;font-size:11.5px;font-family:ui-monospace,Menlo,monospace;background:#f3efe4;border:1px solid var(--line);border-radius:5px;padding:4px 8px;cursor:pointer;color:var(--ink)}}
.key.ok{{background:var(--acc);color:#fff;border-color:var(--acc)}}
.cc.po{{border-style:dashed}}
@media(max-width:860px){{.grid{{grid-template-columns:1fr 1fr}}}}
@media(max-width:560px){{.wrap{{padding:22px 16px 44px}} .grid{{grid-template-columns:1fr;gap:12px}} .how{{font-size:13.5px}}}}
</style></head><body><div class="wrap">
<p class="kicker">Course picker · model courses</p>
<h1>モデルコース棚</h1>
<p class="lead">これまでゲストに出したコース選択ページの全コース。{pages}ページ・{n}コース。緑枠は採用されたコース。ジャンルは1コースに複数付きます。</p>
<div class="how"><b>使い回し方</b>Claudeに「モデルコース棚から〇〇っぽいのを出して」と言えば候補が出ます。気に入ったコースの <code>ページ名:記号</code> をタップしてコピーし、「これで新しい提案ページ作って」と渡せば、たたき台がすぐ出来ます。</div>
{('<p class="fl">作ったプラン</p><ul class="plans">' + ''.join(f'<li><a href="plans/{e(sl)}/" target="_blank" rel="noopener">{e(t)}</a></li>' for sl, t in PLANS) + '</ul>') if PLANS else ''}
<input id="q" type="search" placeholder="絞り込み（例: asakusa / teamlab / rick / ramen）" autocomplete="off">
<p class="fl">ジャンル</p><div class="genres" data-f="g"><button type="button" class="on" data-v="">すべて</button>{''.join(f'<button type="button" data-v="{e(g)}">{e(g)} <i>{n}</i></button>' for g, n in GC.most_common())}</div>
<p class="fl">エリア</p><div class="genres" data-f="a"><button type="button" class="on" data-v="">すべて</button>{''.join(f'<button type="button" data-v="{e(g)}">{e(g)} <i>{n}</i></button>' for g, n in AC.most_common())}</div>
<p class="count" id="count"></p>
<div class="grid" id="grid">{''.join(card(r) for r in rows)}</div>
</div>
<div class="bar" id="bar" hidden><span id="barn"></span><button type="button" id="make">新しいプランを作る</button></div>
<dialog id="dlg"><form class="dlg" method="dialog">
<h2>新しいプランを作る</h2><p class="note" style="margin:0">選んだ順に A・B・C… になります。</p><ol id="dl"></ol>
<label>ゲスト名（英語）</label><input id="f-guest" placeholder="Patrick" required>
<label>日付</label><input id="f-date" type="date" required>
<div class="two"><div><label>開始</label><input id="f-start" type="time" value="10:00"></div><div><label>終了（目安）</label><input id="f-end" type="time" value="15:00"></div></div>
<label>集合場所（英語・Googleマップで引ける名前）</label><input id="f-meet" placeholder="Mitsui Garden Hotel Nihonbashi Premier">
<button type="button" class="go" id="gh">GitHubで作成する</button>
<button type="button" class="sub" id="cl">Claude向けの依頼文をコピー</button>
<button type="button" class="sub" id="cx">閉じる</button>
<p class="note">「GitHubで作成する」を押すと入力済みの画面が開きます。そこで緑の送信ボタンを押すと1〜2分でページができ、URLが返信されます。</p>
</form></dialog>
<script>
var q=document.getElementById('q'),cs=[].slice.call(document.querySelectorAll('.cc')),ct=document.getElementById('count');
var sel={{g:'',a:''}};
document.querySelectorAll('.genres').forEach(function(row){{var bs=[].slice.call(row.querySelectorAll('button')),k=row.dataset.f;
 bs.forEach(function(b){{b.addEventListener('click',function(){{sel[k]=(sel[k]===b.dataset.v)?'':b.dataset.v;bs.forEach(function(x){{x.classList.toggle('on',x.dataset.v===sel[k])}});f()}})}})}});
function has(c,k){{return !sel[k]||(c.dataset[k]||'').split('|').indexOf(sel[k])>=0}}
function f(){{var w=q.value.toLowerCase().split(/\\s+/).filter(Boolean),n=0;cs.forEach(function(c){{var s=c.dataset.q.toLowerCase(),ok=w.every(function(x){{return s.indexOf(x)>=0}})&&has(c,'g')&&has(c,'a');c.hidden=!ok;if(ok)n++}});ct.textContent=n+' 件'}}
q.addEventListener('input',f);f();
document.querySelectorAll('.key').forEach(function(b){{b.addEventListener('click',function(){{navigator.clipboard.writeText(b.dataset.k).then(function(){{b.classList.add('ok');var t=b.textContent;b.textContent='コピーした';setTimeout(function(){{b.classList.remove('ok');b.textContent=t}},1200)}})}})}});
var picked=[],bar=document.getElementById('bar'),dlg=document.getElementById('dlg');
function paint(){{cs.forEach(function(c){{var i=picked.indexOf(c.dataset.k);c.classList.toggle('sel',i>=0);var p=c.querySelector('.pick');if(p)p.textContent=i>=0?'✓ '+String.fromCharCode(65+i)+' として選択中（外す）':'＋ このコースを選ぶ'}});
 bar.hidden=!picked.length;document.body.classList.toggle('has-bar',!!picked.length);document.getElementById('barn').textContent=picked.length+'コース選択中'}}
document.querySelectorAll('.pick').forEach(function(p){{p.addEventListener('click',function(){{var k=p.closest('.cc').dataset.k,i=picked.indexOf(k);if(i>=0)picked.splice(i,1);else if(picked.length<6)picked.push(k);paint()}})}});
function nm(k){{var c=document.querySelector('.cc[data-k="'+k+'"]');return c?c.dataset.n:k}}
document.getElementById('make').addEventListener('click',function(){{document.getElementById('dl').innerHTML=picked.map(function(k){{return '<li>'+nm(k).replace(/</g,'&lt;')+' <small>('+k+')</small></li>'}}).join('');dlg.showModal()}});
document.getElementById('cx').addEventListener('click',function(){{dlg.close()}});
function req(){{var v=function(id){{return document.getElementById(id).value.trim()}};var gst=v('f-guest'),dt=v('f-date');
 return {{slug:(gst+'-'+dt).toLowerCase(),guest:gst,date:dt,start:v('f-start'),end:v('f-end'),meet:v('f-meet'),keys:picked.slice()}}}}
document.getElementById('gh').addEventListener('click',function(){{var r=req();if(!r.guest||!r.date){{alert('ゲスト名と日付を入れてください');return}}
 var body='このまま送信すると、選んだコースで新しい選択ページが作られます（ユウキ本人の送信だけ動きます）。\\n\\n```json\\n'+JSON.stringify(r,null,1)+'\\n```';
 window.open('https://github.com/Yukitchy/course-picker/issues/new?title='+encodeURIComponent('[new-plan] '+r.slug)+'&body='+encodeURIComponent(body),'_blank','noopener')}});
document.getElementById('cl').addEventListener('click',function(){{var r=req();var t='モデルコース棚からこの組み合わせで新しい提案ページを作って: '+r.keys.join(' ')+' / ゲスト '+r.guest+' / '+r.date+' '+r.start+'〜'+r.end+' / 集合 '+r.meet;
 navigator.clipboard.writeText(t).then(function(){{var b=document.getElementById('cl');b.textContent='コピーした';setTimeout(function(){{b.textContent='Claude向けの依頼文をコピー'}},1500)}})}});
</script></body></html>'''
open(ROOT / 'index.html', 'w').write(page)
print('catalog ->', ROOT / 'index.html', n, 'courses')
