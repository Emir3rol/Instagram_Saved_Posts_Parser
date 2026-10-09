"""data/saved.json + data/analysis.json + data/analiz/*.tsv + data/transcripts → rapor.html
--compact: analiz edilmemiş ve transkripti hazır öğeleri Claude'un okuyacağı kısa satırlara döker (data/compact.jsonl).
analysis.json: {"kategoriler": [...], "konu_ozetleri": {kat: metin}}
analiz/*.tsv satırı: code<TAB>kategori_no(1'den)<TAB>puan(1-5)<TAB>özet<TAB>gerekçe"""
import html, json, sys
from collections import Counter
from datetime import date
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

D = Path('data')
items = list({x['code']: x for x in json.load(open(D / 'saved.json', encoding='utf-8'))['items']}.values())
A = json.load(open(D / 'analysis.json', encoding='utf-8')) if (D / 'analysis.json').exists() else {}
an = {}
for f in sorted((D / 'analiz').glob('*.tsv')):
    for satir_ in f.read_text(encoding='utf-8').splitlines():
        if satir_.strip():
            c, k, p, oz, ge = (satir_.split('\t') + [''] * 5)[:5]
            if not (k.isdigit() and p.isdigit()):  # başka araçtan gelen başlık/bozuk satır
                continue
            an[c] = {'kategori': A['kategoriler'][int(k) - 1], 'puan': int(p), 'ozet': oz, 'gerekce': ge}


def transkript(x):
    f = D / 'transcripts' / f"{x['code']}.txt"
    return f.read_text(encoding='utf-8').strip() if f.exists() else ''


if '--compact' in sys.argv:
    # transkripti olanlar önce: en zengin içerik önce işlenir
    with open(D / 'compact.jsonl', 'w', encoding='utf-8') as f:
        for x in sorted(items, key=lambda x: not transkript(x)):
            if x['code'] in an:
                continue
            r = {'c': x['code'], 't': x['tur'], 'u': x['kullanici'], 'a': x['altyazi'][:400],
                 's': transkript(x)[:1000], 'g': x['alt_text'][:150], 'k': x['koleksiyon']}
            f.write(json.dumps({k: v for k, v in r.items() if v}, ensure_ascii=False) + '\n')
    sys.exit()

e = lambda s: html.escape(str(s or ''), quote=True)
puan = lambda x: an.get(x['code'], {}).get('puan', 0)
kat = lambda x: an.get(x['code'], {}).get('kategori', '')
sayi = lambda n: f'{n:,}'.replace(',', '.')
AY = 'Oca Şub Mar Nis May Haz Tem Ağu Eyl Eki Kas Ara'.split()
tarih = lambda t: f"{int(t[8:10])} {AY[int(t[5:7]) - 1]} {t[:4]}" if t and len(t) >= 10 else ''
ONEM = {5: 'Mutlaka bak', 4: 'İşe yarar', 3: 'İlginç', 2: 'Zayıf', 1: 'Mizah ve gereksiz', 0: 'Puansız'}

# 24×24 çizgi simgeler (tek <svg> sprite, <use> ile çağrılır)
SIMGE = {
    'ara': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'gunes': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'ay': '<path d="M20.5 13.2A8.5 8.5 0 1 1 10.8 3.5a6.6 6.6 0 0 0 9.7 9.7z"/>',
    'oynat': '<path d="M8 5.6v12.8a.8.8 0 0 0 1.2.7l10.3-6.4a.8.8 0 0 0 0-1.4L9.2 4.9A.8.8 0 0 0 8 5.6z" fill="currentColor" stroke="none"/>',
    'reel': '<rect x="3" y="3" width="18" height="18" rx="5"/><path d="M3 8.5h18M9 3l3 5.5M15 3l3 5.5"/><path d="M10.5 12.2v4.6l4-2.3z" fill="currentColor"/>',
    'foto': '<rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="9" cy="9" r="1.8"/><path d="m20.5 15.5-4.8-4.8L5 21"/>',
    'album': '<rect x="7.5" y="3" width="13.5" height="13.5" rx="3"/><path d="M16.5 21H6a3 3 0 0 1-3-3V7.5"/>',
    'video': '<rect x="2.5" y="6" width="13.5" height="12" rx="3"/><path d="m16 10.5 5.5-3v9l-5.5-3"/>',
    'yildiz': '<path d="m12 3.2 2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.5l6-.8z" fill="currentColor" stroke="none"/>',
    'kayit': '<path d="M6.5 3h11a1 1 0 0 1 1 1v17l-6.5-4.2L5.5 21V4a1 1 0 0 1 1-1z" fill="currentColor" stroke="none"/>',
    'dis': '<path d="M14 4h6v6M20 4l-8.5 8.5M18 14v4.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10"/>',
    'yukari': '<path d="m6 15 6-6 6 6"/>', 'asagi': '<path d="m6 9 6 6 6-6"/>', 'kapat': '<path d="M6 6l12 12M18 6 6 18"/>',
    'tik': '<path d="m4.5 12.5 5 5L19.5 7"/>', 'geri': '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
    'cop': '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/>',
}
sprite = ('<svg width=0 height=0 style="position:absolute" aria-hidden=true>' + ''.join(
    f'<symbol id=i-{k} viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=1.8 stroke-linecap=round stroke-linejoin=round>{v}</symbol>'
    for k, v in SIMGE.items()) + '</svg>')
ik = lambda n, c='': f"<svg class='ik {c}'><use href=#i-{n} /></svg>"
TUR_IK = {'Reel': 'reel', 'Video': 'video', 'Fotoğraf': 'foto', 'Albüm': 'album'}
resim = lambda c, yer: f"{ik(yer, 'yer')}<img loading=lazy decoding=async src='/t/{e(c)}' alt='' onerror='this.remove()'>"


def kart(x):
    a, p, c = an.get(x['code'], {}), puan(x), x['code']
    sinirli = ("<span class=w title='Videonun sesi yazıya dökülmedi, özet gönderi açıklamasından çıkarıldı.'>ses dökümü yok</span>"
               if x['ses_urls'] and not transkript(x) else '')
    return (f"<article class=pk data-c='{e(c)}' data-k='{e(a.get('kategori'))}' data-p={p} data-t='{e(x['tur'])}' title='{e(a.get('gerekce'))}'>"
            f"<div class=th>{resim(c, TUR_IK.get(x['tur'], 'foto'))}<span class='rozet p{p}'>{ik('yildiz')}{p}</span>"
            f"<span class=turik title='{e(x['tur'])}'>{ik(TUR_IK.get(x['tur'], 'foto'))}</span><span class=oynat>{ik('oynat')}</span>"
            f"<span class=tutik title=Tuttun>{ik('tik')}</span></div>"
            f"<p class=oz>{e(a.get('ozet') or x['altyazi'][:200])}</p>"
            f"<div class=mt><span class=et>{e(a.get('kategori', '-'))}</span>{sinirli}</div>"
            f"<div class=mt><a href='{e(x['url'])}' target=_blank rel=noopener title='Instagram’da aç'>@{e(x['kullanici'])}</a><span>{tarih(x['tarih'])}</span></div>"
            f"<button class=geri title='Çöp kutusundan çıkar'>{ik('geri')}Geri al</button></article>")


kats = [k for k in A.get('kategoriler', []) if k not in ('Diğer', 'Mizah')] + [k for k in ('Diğer', 'Mizah') if k in A.get('kategoriler', [])]
kat_say = Counter(kat(x) for x in items if x['code'] in an)
onemli = Counter(kat(x) for x in items if puan(x) >= 4)
tur_say = Counter(x['tur'] for x in items)
sirali = sorted(items, key=lambda x: (-puan(x), kat(x) == 'Mizah'))

gruplar = ''.join(
    f"<section class=grup data-g={p}><h3>{ONEM[p]}<span class=yz>{'★' * p}</span><span class=gs></span></h3>"
    f"<div class=izgara>{''.join(kart(x) for x in sirali if puan(x) == p)}</div></section>"
    for p in sorted({puan(x) for x in items}, reverse=True))
koller = ''.join(
    f"<div class=kol data-kat='{e(k)}'><div class=moz>"
    + ''.join(f"<span>{resim(x['code'], 'foto')}</span>" for x in [x for x in sirali if kat(x) == k][:4])
    + f"<button class=kizle data-kat='{e(k)}' title='Bu konuyu sırayla izle'>{ik('oynat')}</button></div>"
      f"<div class=kb><b>{e(k)}</b><small>{kat_say[k]} gönderi · {onemli[k]} önemli</small></div></div>" for k in kats)
p_onem = ''.join(f"<button data-y={y}>{ik('yildiz') if y else ''}{t}<i></i></button>" for y, t in [(0, 'Hepsi'), (5, '5'), (4, '4+'), (3, '3+'), (2, '2+')])
p_tur = "<button data-tur=''>Hepsi<i></i></button>" + ''.join(f"<button data-tur='{e(t)}' title='{e(t)}'>{ik(TUR_IK.get(t, 'foto'))}{e(t)}<i></i></button>" for t, _ in tur_say.most_common())
p_durum = ''.join(f"<button data-u='{u}'>{ik(s) if s else ''}{t}<i></i></button>" for u, s, t in
                  [('', '', 'Hepsi'), ('yeni', '', 'İncelenmedi'), ('tut', 'tik', 'Tutulan'), ('sil', 'cop', 'Çöp kutusu')])
p_kat = "<button class=cip data-kat=''>Tüm konular<i></i></button>" + ''.join(f"<button class=cip data-kat='{e(k)}'>{e(k)}<i></i></button>" for k in kats)
kunye = (f"Derlendi: {tarih(str(date.today()))}. {sayi(sum(1 for x in items if transkript(x)))} videonun sesi yazıya döküldü; "
         f"diğerlerinin özeti gönderi açıklamasından çıkarıldı. Konular, özetler ve önem puanları Claude'un.")
ozet_js = json.dumps(A.get('konu_ozetleri', {}), ensure_ascii=False).replace('</', '<\\/')

Path('rapor.html').write_text(f"""<!doctype html><html lang=tr><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Kaydedilenler</title>
<script>try{{const t=localStorage.getItem('tema');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script><style>
:root{{color-scheme:dark;--bg:#0e0f11;--s1:#16181b;--s2:#1e2125;--s3:#2b2f35;--line:#272a30;--fg:#ebecee;--mut:#8d929a;--acc:#ff5f3c;--w:#e6b04d;--r:12px;
 --font:"Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,sans-serif}}
:root[data-theme=light]{{color-scheme:light;--bg:#f6f6f4;--s1:#fff;--s2:#ececea;--s3:#d6d6d2;--line:#e2e2de;--fg:#17181b;--mut:#686d75;--acc:#e64a2b;--w:#94670a}}
[hidden]{{display:none!important}} *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:14.5px/1.5 var(--font);-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}} button{{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}}
:focus-visible{{outline:2px solid var(--acc);outline-offset:2px;border-radius:6px}} ::selection{{background:var(--acc);color:#fff}}
.ik{{width:18px;height:18px;flex:none}} .wrap{{max-width:1240px;margin:auto;padding:0 28px}}
.ust{{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:saturate(1.4) blur(14px);border-bottom:1px solid var(--line)}}
.bar{{display:flex;align-items:center;gap:22px;height:64px}}
.marka{{display:flex;align-items:center;gap:10px;font-size:16px;font-weight:650;letter-spacing:-.01em;white-space:nowrap}}
.logo{{display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:var(--acc);color:#fff}} .logo .ik{{width:15px;height:15px}}
.ara{{flex:1;max-width:540px;display:flex;align-items:center;gap:10px;height:40px;padding:0 12px;border-radius:10px;background:var(--s2);border:1px solid transparent;color:var(--mut);transition:border-color .15s,background .15s}}
.ara:focus-within{{border-color:var(--acc);background:var(--s1)}} #q{{flex:1;min-width:0;border:0;background:none;outline:0;color:var(--fg);font:inherit}}
kbd{{font:11px/1 ui-monospace,Consolas,monospace;color:var(--mut);border:1px solid var(--s3);border-radius:5px;padding:3px 6px}}
.ikbtn{{display:grid;place-items:center;width:38px;height:38px;border-radius:10px;color:var(--mut)}} .ikbtn:hover{{background:var(--s2);color:var(--fg)}}
#tema .a,[data-theme=light] #tema .g{{display:none}} [data-theme=light] #tema .a{{display:block}}
.filtre{{display:flex;align-items:center;gap:10px 12px;flex-wrap:wrap;padding:2px 0 12px}}
.seg{{display:flex;gap:2px;padding:3px;background:var(--s2);border-radius:10px;max-width:100%;overflow-x:auto;scrollbar-width:none}}
.seg button{{display:flex;align-items:center;gap:6px;height:30px;padding:0 11px;border-radius:7px;color:var(--mut);font-size:13.5px;white-space:nowrap;transition:background .15s,color .15s}}
.seg button:hover{{color:var(--fg)}} .seg button.on{{background:var(--s1);color:var(--fg);box-shadow:0 1px 2px #00000030,0 0 0 1px var(--line)}}
.seg .ik{{width:15px;height:15px}} #onemler .ik{{width:13px;height:13px;color:#ffc24b}} .seg i,.cip i{{font-style:normal;font-size:11.5px;color:var(--mut);font-variant-numeric:tabular-nums}}
.sifir{{opacity:.38}} #temizle{{margin-left:auto;color:var(--mut);font-size:13px}} #temizle:hover{{color:var(--fg)}}
.ana{{margin-left:auto;display:flex;align-items:center;gap:8px;height:36px;padding:0 16px 0 13px;border-radius:10px;background:var(--acc);color:#fff;font-weight:600;white-space:nowrap;transition:filter .15s}}
.ana:hover{{filter:brightness(1.08)}} .ana:disabled{{opacity:.4;cursor:default}} .ana .ik{{width:14px;height:14px}}
.cipler{{display:flex;gap:6px;overflow-x:auto;padding:0 0 12px;scrollbar-width:none;mask-image:linear-gradient(90deg,#000 93%,transparent)}}
.cip{{flex:none;display:flex;align-items:center;gap:6px;height:30px;padding:0 12px;border-radius:999px;border:1px solid var(--line);color:var(--mut);font-size:13px;white-space:nowrap;transition:.15s}}
.cip:hover{{color:var(--fg);border-color:var(--s3)}} .cip.on{{background:var(--fg);border-color:var(--fg);color:var(--bg)}} .cip.on i{{color:var(--bg);opacity:.65}}
#uyari{{display:flex;gap:10px;align-items:center;margin-top:16px;padding:12px 16px;border-radius:var(--r);background:color-mix(in srgb,var(--w) 12%,transparent);color:var(--w)}}
h2{{display:flex;align-items:baseline;gap:10px;margin:34px 0 16px;font-size:20px;font-weight:650;letter-spacing:-.01em;scroll-margin-top:calc(var(--ph,0px) + 14px)}} h2 small{{font-size:13px;font-weight:400;color:var(--mut)}}
.koller{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:22px 18px}} .kol{{cursor:pointer;min-width:0}}
.moz{{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:2px;aspect-ratio:1;border-radius:var(--r);overflow:hidden;background:var(--s2);transition:transform .2s}}
.moz>span,.th{{position:relative;display:grid;place-items:center;background:var(--s2);overflow:hidden}} .yer{{width:24px;height:24px;color:var(--s3)}}
.moz img,.th img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.kol:hover .moz{{transform:translateY(-3px)}} .kol.on .moz{{outline:2px solid var(--acc);outline-offset:3px}}
.kizle{{position:absolute;right:8px;bottom:8px;display:grid;place-items:center;width:38px;height:38px;border-radius:50%;background:var(--acc);color:#fff;opacity:0;transform:translateY(6px);transition:.18s;box-shadow:0 6px 16px #0007}}
.kizle .ik{{width:15px;height:15px;margin-left:2px}} .kol:hover .kizle,.kizle:focus-visible{{opacity:1;transform:none}}
.kb{{padding:10px 2px 0}} .kb b{{display:block;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .kb small{{color:var(--mut);font-size:12.5px}}
#konu{{margin-top:30px;padding:20px 24px;border-radius:var(--r);background:var(--s1);border:1px solid var(--line)}} #konu h2{{margin:0 0 6px}} #konu p{{margin:0;color:var(--mut);line-height:1.65;max-width:95ch}}
.grup h3{{position:sticky;top:var(--ph,0px);z-index:2;display:flex;align-items:center;gap:10px;margin:0;padding:18px 0 12px;background:var(--bg);font-size:15px;font-weight:650}}
.yz{{color:var(--acc);font-size:11px;letter-spacing:1.5px}} .gs{{color:var(--mut);font-weight:400;font-size:13px}}
.izgara{{display:grid;grid-template-columns:repeat(auto-fill,minmax(184px,1fr));gap:24px 18px;padding-bottom:18px}}
.pk{{cursor:pointer;min-width:0}} .th{{aspect-ratio:4/5;border-radius:var(--r)}} .th img{{transition:transform .35s}} .pk:hover .th img{{transform:scale(1.035)}}
.rozet{{position:absolute;left:8px;top:8px;display:flex;align-items:center;gap:3px;height:22px;padding:0 7px 0 5px;border-radius:6px;background:#000000a8;color:#fff;font-size:12px;font-weight:600;backdrop-filter:blur(6px)}}
.rozet .ik{{width:12px;height:12px;color:#ffc24b}} .rozet.p5{{background:var(--acc)}} .rozet.p5 .ik{{color:#fff}} .rozet.p1,.rozet.p0{{display:none}}
.turik{{position:absolute;right:9px;top:9px;color:#fff;filter:drop-shadow(0 1px 3px #000a)}}
.oynat{{position:absolute;inset:0;margin:auto;display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#ffffffe8;color:#111;opacity:0;transform:scale(.88);transition:.18s;box-shadow:0 6px 20px #0006}}
.oynat .ik{{width:18px;height:18px;margin-left:2px}} .pk:hover .oynat{{opacity:1;transform:none}}
.pk .oz{{margin:10px 2px 4px;font-size:14px;line-height:1.42;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.mt{{display:flex;flex-wrap:wrap;gap:1px 10px;margin:0 2px;font-size:12.5px;color:var(--mut)}} .mt a{{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}} .mt a:hover{{color:var(--acc)}} .et{{color:var(--fg);opacity:.72}}
.w{{text-decoration:underline dotted;text-underline-offset:3px;cursor:help}}
.tutik{{position:absolute;right:8px;bottom:8px;display:none;place-items:center;width:26px;height:26px;border-radius:50%;background:#2fbf71;color:#fff;box-shadow:0 2px 8px #0006}}
.tutik .ik{{width:15px;height:15px;stroke-width:2.6}} .pk[data-d=tut] .tutik{{display:grid}} .pk[data-d=sil] .th{{opacity:.55}}
.geri{{display:none;align-items:center;gap:6px;margin:8px 2px 0;height:30px;padding:0 12px;border-radius:8px;background:var(--s2);font-size:13px}} .geri:hover{{background:var(--s3)}}
.geri .ik{{width:15px;height:15px}} .pk[data-d=sil] .geri{{display:inline-flex}} #durumlar button[data-u=sil] .ik{{color:#ff6b5e}} #durumlar button[data-u=tut] .ik{{color:#2fbf71}}
#bildirim{{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:10;display:flex;align-items:center;gap:16px;padding:10px 12px 10px 16px;border-radius:12px;background:#26292e;color:#f2f2f2;font-size:14px;white-space:nowrap;box-shadow:0 10px 30px #0008}}
#bildirim button{{color:#ff8a6b;font-weight:600}} dialog #bildirim{{top:18px;bottom:auto}}
#bos{{padding:64px 0;text-align:center;color:var(--mut)}} footer{{margin:48px 0 0;padding:18px 0 56px;border-top:1px solid var(--line);color:var(--mut);font-size:13px}}
dialog{{padding:0;border:0;margin:0;width:100vw;height:100vh;max-width:100vw;max-height:100vh;background:#0b0b0c;color:#eee}} dialog::backdrop{{background:#0b0b0c}} html:has(dialog[open]){{overflow:hidden}}
#fd{{height:100%;overflow-y:auto;scroll-snap-type:y mandatory;overscroll-behavior:contain;scrollbar-width:none}}
#fd section{{height:100%;scroll-snap-align:start;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px}}
.st{{position:relative;height:calc(100% - 108px);aspect-ratio:9/16;max-width:calc(100vw - 160px);border-radius:14px;overflow:hidden;background:#000;touch-action:pan-y;transition:transform .26s ease-out}}
.kr{{display:flex;gap:30px}} .kr button{{display:grid;place-items:center;width:58px;height:58px;border-radius:50%;background:#ffffff10;border:1px solid #ffffff24;transition:background .15s,transform .15s}}
.kr button:hover{{transform:scale(1.06)}} .kr .ik{{width:24px;height:24px;stroke-width:2.2}} .ksil{{color:#ff6b5e}} .ktut{{color:#3ddc84}}
section[data-d=sil] .ksil{{background:#ff6b5e;border-color:#ff6b5e;color:#160805}} section[data-d=tut] .ktut{{background:#3ddc84;border-color:#3ddc84;color:#04170c}}
.damga{{position:absolute;top:30px;z-index:2;padding:4px 12px;border:3px solid;border-radius:8px;font-size:26px;font-weight:800;letter-spacing:2px;opacity:0;pointer-events:none}}
.damga.tut{{left:18px;color:#3ddc84;transform:rotate(-12deg)}} .damga.sil{{right:18px;color:#ff6b5e;transform:rotate(12deg)}}
section[data-d=tut] .damga.tut,section[data-d=sil] .damga.sil{{opacity:1}} .st{{-webkit-user-select:none;user-select:none}}
.st video,.st iframe{{position:absolute;inset:0;width:100%;height:100%;border:0;background:#000}} .st iframe{{background:#fff}}
.bilgi{{position:absolute;left:0;right:0;bottom:0;z-index:1;padding:64px 16px 60px;background:linear-gradient(transparent,#000000db 42%);pointer-events:none;font-size:13px}}
.st:has(iframe) .bilgi{{padding-bottom:16px}} .bilgi .oz{{margin:0 0 6px;color:#f4f4f4;font-size:14.5px;cursor:pointer;pointer-events:auto;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.bilgi .oz.acik{{-webkit-line-clamp:unset}} .bilgi .mt{{margin:0;color:#b9b9b9;pointer-events:auto}} .bilgi .et{{color:#fff}} .bilgi .onem{{color:#ff8a6b;font-weight:600}}
#sayac{{position:fixed;top:22px;left:26px;font:12px ui-monospace,Consolas,monospace;color:#8a8a8a}}
.fk{{position:fixed;top:16px;right:22px}} .fk button,.fn button{{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;background:#ffffff14;color:#ddd;transition:background .15s}}
.fk button:hover,.fn button:hover{{background:#ffffff2e;color:#fff}} .fn{{position:fixed;right:22px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:10px}}
#tus{{position:fixed;bottom:20px;left:26px;font:12px/1.9 ui-monospace,Consolas,monospace;color:#666}} #ipucu{{position:fixed;top:44px;left:26px;font-size:13px;color:#e6b04d}}
@media (max-width:720px){{.wrap{{padding:0 16px}} .ust{{position:static}} .bar{{flex-wrap:wrap;height:auto;padding:12px 0;gap:12px}} .ara{{order:3;flex-basis:100%;max-width:none}}
 .izgara{{grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 12px}} .koller{{grid-template-columns:repeat(2,minmax(0,1fr))}}
 .oynat,.kizle{{display:none}} #tus{{display:none}} .st{{width:100%;max-width:none;aspect-ratio:auto;height:calc(100% - 86px);border-radius:0}} #fd section{{justify-content:flex-start;gap:12px}} .fn{{right:10px}}}}
</style>
{sprite}
<dialog id=d><div id=fd></div><span id=sayac></span><div id=ipucu hidden>Otomatik oynatma kapalı. Raporu baslat.bat ile açınca açılır.</div>
<div class=fk><form method=dialog><button title="Kapat (Esc)">{ik('kapat')}</button></form></div>
<div id=tus>→ tut<br>← çöp kutusu<br>↑ ↓ geç<br>boşluk durdur<br>M ses<br>Esc kapat</div>
<div class=fn><button id=yuk title="Önceki (↑)">{ik('yukari')}</button><button id=asg title="Sonraki (↓)">{ik('asagi')}</button></div></dialog>
<div class=ust id=panel><div class=wrap>
 <div class=bar><div class=marka><span class=logo>{ik('kayit')}</span>Kaydedilenler</div>
  <label class=ara>{ik('ara')}<input id=q type=search placeholder="Gönderi, kullanıcı ya da konu ara" aria-label=Ara><kbd title="Aramaya atla">/</kbd></label>
  <button id=iz class=ana>{ik('oynat')}<span>Sırayla izle</span></button><button id=tema class=ikbtn title="Açık / koyu tema">{ik('gunes', 'g')}{ik('ay', 'a')}</button></div>
 <div class=filtre><div class=seg id=onemler title=Önem>{p_onem}</div><div class=seg id=turler title=Tür>{p_tur}</div><div class=seg id=durumlar title=Durum hidden>{p_durum}</div>
  <button id=temizle hidden>Filtreleri temizle</button></div>
 <div class=cipler id=katlar>{p_kat}</div>
</div></div>
<main class=wrap>
<div id=uyari hidden>{ik('video')}Videolar kendiliğinden oynamayacak ve kapaklar görünmeyecek, çünkü rapor dosyadan açıldı. Bu sekmeyi kapatıp klasördeki baslat.bat'ı çalıştır.</div>
<h2>Konular<small>{len(kats)} koleksiyon</small></h2><div class=koller>{koller}</div>
<div id=konu hidden><h2></h2><p></p></div>
<h2 id=liste>Gönderiler<small>en önemliden aşağı</small></h2>{gruplar}<p id=bos hidden>Bu filtrelerle gönderi kalmadı.</p>
<footer>{e(kunye)}</footer>
</main><div id=bildirim hidden></div>
<script>
const OZET={ozet_js},ONEM={json.dumps(ONEM, ensure_ascii=False)},IK={json.dumps({'cop': ik('cop'), 'tik': ik('tik')})},fmt=n=>n.toLocaleString('tr-TR');
const S={{q:'',k:'',y:0,t:'',u:''}},R=[...document.querySelectorAll('.pk')].map(r=>({{r,s:r.textContent.toLocaleLowerCase('tr'),k:r.dataset.k,p:+r.dataset.p,t:r.dataset.t,d:''}})),
 RC=new Map(R.map(x=>[x.r.dataset.c,x])),G=[...document.querySelectorAll('.grup')],kH=konu.querySelector('h2'),kP=konu.querySelector('p');
// tek geçişte kartları süzer, filtre sayılarını da o anki diğer filtrelere göre günceller
// x.d: '' incelenmedi, 'tut', 'sil' (çöp kutusu: yalnız "Çöp kutusu" seçiliyken görünür)
function f(){{const ck={{'':0}},cy=[0,0,0,0,0,0],ct={{'':0}},cd={{'':0,yeni:0,tut:0,sil:0}},cg={{}};let n=0;
 for(const x of R){{const q=x.s.includes(S.q),k=!S.k||x.k==S.k,y=x.p>=S.y,t=!S.t||x.t==S.t,
   u=S.u=='sil'?x.d=='sil':x.d!='sil'&&(!S.u||S.u==(x.d||'yeni'));
  if(q&&y&&t&&u){{ck['']++;ck[x.k]=(ck[x.k]||0)+1}} if(q&&k&&t&&u)cy[x.p]++; if(q&&k&&y&&u){{ct['']++;ct[x.t]=(ct[x.t]||0)+1}}
  if(q&&k&&y&&t){{if(x.d=='sil')cd.sil++;else{{cd['']++;cd[x.d||'yeni']++}}}}
  const g=q&&k&&y&&t&&u;x.r.hidden=!g;if(g){{n++;cg[x.p]=(cg[x.p]||0)+1}}}}
 const yay=(sel,say,aktif)=>document.querySelectorAll(sel).forEach(b=>{{const c=say(b);b.lastChild.textContent=fmt(c);b.classList.toggle('sifir',!c);b.classList.toggle('on',aktif(b))}});
 yay('#katlar button',b=>ck[b.dataset.kat]||0,b=>b.dataset.kat==S.k);
 yay('#onemler button',b=>cy.reduce((a,c,p)=>a+(p>=+b.dataset.y?c:0),0),b=>+b.dataset.y==S.y);
 yay('#turler button',b=>ct[b.dataset.tur]||0,b=>b.dataset.tur==S.t);
 yay('#durumlar button',b=>cd[b.dataset.u],b=>b.dataset.u==S.u);
 liste.lastChild.textContent=S.u=='sil'?'çöp kutusu · sağa atınca ya da Geri al ile listeye döner':'en önemliden aşağı';
 document.querySelectorAll('.kol').forEach(c=>c.classList.toggle('on',c.dataset.kat==S.k));
 G.forEach(g=>{{const c=cg[g.dataset.g]||0;g.hidden=!c;g.querySelector('.gs').textContent=fmt(c)+' gönderi'}});
 konu.hidden=!S.k;kH.textContent=S.k;kP.textContent=OZET[S.k]||'';
 iz.lastChild.textContent=fmt(n)+' gönderiyi izle';bos.hidden=n>0;iz.disabled=!n;temizle.hidden=!(S.q||S.k||S.y||S.t||S.u)}}
const listeye=()=>(S.k?konu:liste).scrollIntoView({{behavior:'smooth'}});
// yapışkan başlıklar ve kaydırma payı üst panelin yüksekliğine göre (mobilde panel yapışkan değil → 0)
const ph=()=>document.documentElement.style.setProperty('--ph',(getComputedStyle(panel).position=='sticky'?panel.offsetHeight:0)+'px');
new ResizeObserver(ph).observe(panel);onresize=ph;
konu.style.scrollMarginTop='calc(var(--ph,0px) + 14px)';
q.oninput=()=>{{S.q=q.value.trim().toLocaleLowerCase('tr');f()}};
temizle.onclick=()=>{{Object.assign(S,{{q:'',k:'',y:0,t:'',u:''}});q.value='';f()}};
tema.onclick=()=>{{const t=document.documentElement.dataset.theme=='light'?'dark':'light';document.documentElement.dataset.theme=t;try{{localStorage.setItem('tema',t)}}catch(e){{}}}};
document.onclick=ev=>{{const t=ev.target;if(t.closest('a'))return;
 const oz=t.closest('.bilgi .oz');if(oz)return oz.classList.toggle('acik');
 const kz=t.closest('.kizle');if(kz){{S.k=kz.dataset.kat;f();return izle()}}
 const gb=t.closest('.geri');if(gb)return karar(gb.closest('.pk').dataset.c,'');
 const kb=t.closest('.kr button');if(kb)return at(kb.closest('section'),kb.classList.contains('ktut')?'tut':'sil');
 const pk=t.closest('.pk');if(pk)return izle(pk.dataset.c);
 const kl=t.closest('.kol');if(kl){{S.k=S.k==kl.dataset.kat?'':kl.dataset.kat;f();return listeye()}}
 const b=t.closest('.seg button,.cip');if(!b)return;const v=b.dataset;
 if('kat' in v)S.k=v.kat;else if('y' in v)S.y=+v.y;else if('tur' in v)S.t=v.tur;else if('u' in v)S.u=v.u;f();listeye()}};
document.onkeydown=ev=>{{if(ev.key=='/'&&!d.open&&document.activeElement!=q){{ev.preventDefault();q.focus()}}}};
f();
// izleme: süzülmüş gönderiler, Reels gibi dikey akış
// izle.py ile açıldıysa Reel/Video kendi <video>'muzla oynar (otomatik), yoksa Instagram embed (elle oynat)
const yerel=location.protocol!='file:',SUNUCU='http://127.0.0.1:8765/',ifr=c=>'<iframe scrolling=no allow="autoplay; encrypted-media; fullscreen" src="https://www.instagram.com/p/'+c+'/embed/"></iframe>';
let secs=[],cur=0,sessiz=false;ipucu.hidden=yerel;
// sadece şu anki + sonraki oynatıcı var: önceki kaldırılınca sesi kesilir, sonraki önden yüklenir
const yukle=()=>{{cur=Math.round(fd.scrollTop/fd.clientHeight)||0;sayac.textContent=String(cur+1).padStart(String(secs.length).length,'0')+' / '+secs.length;
 secs.forEach((s,j)=>{{const st=s.firstChild,m=st.querySelector('video,iframe'),yakin=j==cur||j==cur+1;
  if(yakin&&!m){{st.insertAdjacentHTML('afterbegin',yerel&&s.dataset.v?'<video controls loop playsinline preload=auto poster="/t/'+s.dataset.c+'" src="/v/'+s.dataset.c+'"></video>':ifr(s.dataset.c));
   const v=st.firstChild;if(v.tagName=='VIDEO'){{v.muted=sessiz;v.onvolumechange=()=>sessiz=v.muted;v.onerror=()=>{{v.insertAdjacentHTML('afterend',ifr(s.dataset.c));v.remove()}}}}}}
  else if(!yakin&&m)m.remove()}});
 const v=secs[cur]&&secs[cur].querySelector('video');fd.querySelectorAll('video').forEach(x=>x!=v&&x.pause());
 if(v)v.play().catch(()=>{{v.muted=true;v.play().catch(()=>{{}})}})}};
function izle(bas){{secs=R.filter(x=>!x.r.hidden).map(x=>{{const r=x.r,s=document.createElement('section'),m=r.querySelectorAll('.mt');s.dataset.c=r.dataset.c;s.dataset.d=x.d;if(/^(Reel|Video)$/.test(r.dataset.t))s.dataset.v=1;
  s.innerHTML='<div class=st><b class="damga tut">TUT</b><b class="damga sil">SİL</b><div class=bilgi><p class=oz>'+r.querySelector('.oz').innerHTML+'</p><div class=mt><span class=onem>'+ONEM[r.dataset.p]+'</span>'+m[0].innerHTML+m[1].innerHTML+'</div></div></div>'
   +(yerel?'<div class=kr><button class=ksil title="Çöp kutusuna at (←)">'+IK.cop+'</button><button class=ktut title="Tut (→)">'+IK.tik+'</button></div>':'');return s}});
 if(!secs.length)return;fd.replaceChildren(...secs);d.showModal();
 fd.scrollTop=Math.max(0,secs.findIndex(s=>s.dataset.c==bas))*fd.clientHeight;yukle()}}
fd.onscrollend=yukle;d.onclose=()=>{{if(!d.open){{fd.replaceChildren();secs=[]}}}};
const git=y=>fd.scrollBy(0,y*fd.clientHeight);yuk.onclick=()=>git(-1);asg.onclick=()=>git(1);iz.onclick=()=>izle();
// → tut, ← çöp kutusu, ↑/↓ geçiş, boşluk oynat/durdur, M ses (odak videodaysa tarayıcı kendisi halleder)
d.onkeydown=ev=>{{const y={{ArrowDown:1,ArrowUp:-1}}[ev.key];if(y){{ev.preventDefault();git(y);return}}
 const h={{ArrowRight:'tut',ArrowLeft:'sil'}}[ev.key];if(h&&yerel&&secs[cur]){{ev.preventDefault();return at(secs[cur],h)}}
 const v=secs[cur]&&secs[cur].querySelector('video');if(!v||ev.target.tagName=='VIDEO')return;
 if(ev.key==' '){{ev.preventDefault();v.paused?v.play():v.pause()}}else if(ev.key=='m'||ev.key=='M')v.muted=!v.muted}};
// kararlar (Tinder gibi): sağa = tut, sola = çöp kutusu. izle.py'de data/kararlar.json'da durur; Instagram'a dokunulmaz
function karar(c,d,sessizce){{const x=RC.get(c);if(!x||x.d==d)return;const once=x.d,s=secs.find(s=>s.dataset.c==c),koy=v=>{{x.d=v;x.r.dataset.d=v;if(s)s.dataset.d=v;f()}};koy(d);
 fetch('/karar',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{c,d}})}}).then(r=>{{if(!r.ok)throw r;
  if(!sessizce)bildir(d=='sil'?'Çöp kutusuna taşındı':d=='tut'?(once=='sil'?'Çöp kutusundan çıkarıldı':'Tutuldu'):'Listeye geri döndü',()=>karar(c,once,1))}})
 .catch(()=>{{koy(once);bildir('Kaydedilemedi, bağlantını kontrol et')}})}}
let bz;function bildir(m,geri){{bildirim.replaceChildren(m);if(geri){{const b=document.createElement('button');b.textContent='Geri al';b.onclick=()=>{{bildirim.hidden=true;geri()}};bildirim.append(b)}}
 (d.open?d:document.body).append(bildirim);bildirim.hidden=false;clearTimeout(bz);bz=setTimeout(()=>bildirim.hidden=true,4500)}}
// karar verilen gönderi yana uçar, akış sonrakine geçer
function at(s,d){{const st=s.firstChild,y=d=='tut'?1:-1;st.style.transform='translateX('+y*110+'vw) rotate('+y*16+'deg)';karar(s.dataset.c,d);
 setTimeout(()=>{{git(1);setTimeout(()=>{{st.style.transition='none';st.style.transform='';st.offsetHeight;st.style.transition=''}},400)}},240)}}
// sağa/sola sürükleme (fare ya da parmak); dikey hareket akışı kaydırır (touch-action: pan-y)
let sw=null;
fd.onpointerdown=ev=>{{const st=ev.target.closest('.st');sw=yerel&&st&&ev.isPrimary?{{st,x:ev.clientX,y:ev.clientY,dx:0,on:0,id:ev.pointerId}}:null}};
fd.onpointermove=ev=>{{if(!sw||ev.pointerId!=sw.id)return;const dx=ev.clientX-sw.x,dy=ev.clientY-sw.y;
 if(!sw.on){{if(Math.abs(dy)>12&&Math.abs(dy)>Math.abs(dx)){{sw=null;return}}if(Math.abs(dx)<12)return;sw.on=1;try{{sw.st.setPointerCapture(ev.pointerId)}}catch(e){{}}sw.st.style.transition='none'}}
 sw.dx=dx;sw.st.style.transform='translateX('+dx+'px) rotate('+dx/20+'deg)';
 const[tu,si]=sw.st.querySelectorAll('.damga');tu.style.opacity=Math.min(1,Math.max(0,dx/100));si.style.opacity=Math.min(1,Math.max(0,-dx/100))}};
fd.onpointerup=fd.onpointercancel=ev=>{{if(!sw||ev.pointerId!=sw.id)return;const{{st,dx,on}}=sw;sw=null;if(!on)return;
 st.style.transition='';st.querySelectorAll('.damga').forEach(x=>x.style.opacity='');
 if(Math.abs(dx)>100)at(st.parentNode,dx>0?'tut':'sil');else st.style.transform=''}};
// adres #konu=…&onem=4&tur=Reel&durum=yeni&izle[=KOD] → o görünümle açılır (yer imi / paylaşım)
const AH=new URLSearchParams(location.hash.slice(1)),adres=()=>{{if(!AH.size)return;Object.assign(S,{{k:AH.get('konu')||'',y:+AH.get('onem')||0,t:AH.get('tur')||'',u:AH.get('durum')||''}});f();
 if(AH.has('izle'))izle(AH.get('izle'));else if(AH.has('liste'))(S.k?konu:liste).scrollIntoView()}};
if(yerel)fetch('/kararlar').then(r=>r.json()).then(K=>{{for(const x of R){{x.d=K[x.r.dataset.c]||'';x.r.dataset.d=x.d}}durumlar.hidden=false;f();adres()}}).catch(adres);else adres();
// doğrudan açıldıysa: izle.py çalışıyorsa ona geç, çalışmıyorsa uyar
if(!yerel)fetch(SUNUCU,{{mode:'no-cors'}}).then(()=>location.replace(SUNUCU),()=>uyari.hidden=false);
</script></html>""", encoding='utf-8')
print('rapor.html:', len(items), 'öğe,', len(an), 'analizli')
