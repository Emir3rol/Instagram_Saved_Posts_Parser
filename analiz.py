"""Kaydedilenleri Claude API ile analiz eder (Claude oturumunda elle yapılan işin otomatik hali):
1) kategori yoksa örnek gönderilerden önerir, onayını alır → data/analysis.json
2) analiz edilmemiş gönderileri 50'şer: kategori, önem puanı 1–5, özet, gerekçe → data/analiz/NNN.tsv
3) yeni analiz olduysa her konu için özet paragrafı → data/analysis.json
Kaldığı yerden devam eder; yeniden çalıştırınca yalnız yeni kaydedilenler işlenir.
Anahtar: ANTHROPIC_API_KEY ortam değişkeni, yoksa sorar (console.anthropic.com → API Keys).
Kullanım: python analiz.py   (baslat.bat bunu kendisi çağırır)"""
import getpass, json, os, subprocess, sys
from pathlib import Path

import anthropic

sys.stdout.reconfigure(encoding='utf-8')
MODEL = 'claude-opus-5-5'
FIYAT = (4, 20)  # $ / 1M girdi, çıktı token (Opus 5.5)
GRUP = 50
D = Path('data')
AF = D / 'analysis.json'
RUBRIK = """Önem puanı 1–5 (özenle; yalnız açıklamaya değil, varsa transkripte göre):
5: somut, uygulanabilir, kalıcı değeri olan bilgi/teknik (adım adım öğretici, araç, yöntem)
4: faydalı ama daha genel bilgi, iyi kaynak önerisi (kitap/film/araç listesi)
3: ilham, referans, haber, ilginç bilgi
2: zayıf içerik (reklam, klişe motivasyon, içeriği belirsiz)
1: Mizah (meme, şaka, hayvan videoları, eğlence)"""
obje = lambda alanlar: {'type': 'object', 'properties': alanlar, 'required': list(alanlar), 'additionalProperties': False}
METIN = {'type': 'string'}
harcama = [0, 0]
client = None


def sor(sistem, icerik, sema):
    r = client.beta.messages.create(
        model=MODEL, max_tokens=16000, system=sistem, messages=[{'role': 'user', 'content': icerik}],
        output_config={'effort': 'low', 'format': {'type': 'json_schema', 'schema': sema}},  # sınıflandırma: düşük effort yeter
        betas=['server-side-fallback-2026-07-01'], fallbacks='default')  # güvenlik reddinde istek uygun modelde yeniden denenir
    harcama[0] += r.usage.input_tokens
    harcama[1] += r.usage.output_tokens
    if r.stop_reason in ('refusal', 'max_tokens'):
        raise RuntimeError(f'yanıt alınamadı ({r.stop_reason})')
    return json.loads(next(b.text for b in r.content if b.type == 'text'))


def kaydet(A):
    AF.write_text(json.dumps(A, ensure_ascii=False, indent=1), encoding='utf-8')


def bekleyenler():
    subprocess.run([sys.executable, 'build.py', '--compact'], check=True)  # analiz edilmemişler → data/compact.jsonl
    return [json.loads(s) for s in open(D / 'compact.jsonl', encoding='utf-8') if s.strip()]


def analizler():  # code → (kategori_no, puan, özet)
    an = {}
    for f in sorted((D / 'analiz').glob('*.tsv')):
        for s in f.read_text(encoding='utf-8').splitlines():
            p = s.split('\t')
            if len(p) >= 4 and p[1].isdigit() and p[2].isdigit():
                an[p[0]] = (int(p[1]), int(p[2]), p[3])
    return an


def kategori_oner(satirlar):
    adim = max(1, len(satirlar) // 300)
    ornek = '\n'.join(json.dumps({k: r[k][:160] for k in 'tasg' if r.get(k)}, ensure_ascii=False) for r in satirlar[::adim][:300])
    j = sor('Bir kişinin Instagram kaydedilenlerini konulara ayıran bir arşivcisin.',
            'Aşağıda kaydedilen gönderilerden örnekler var (t=tür, a=açıklama, s=transkript, g=görsel açıklaması).\n'
            'Bu kişinin ilgi alanlarını yansıtan 8–13 Türkçe kategori öner. Kısa adlar kullan (ör. "Yemek & Tarif", "Yapay Zeka & Yazılım"). '
            '"Diğer" ve "Mizah" ayrıca eklenecek, onları yazma.\n\n' + ornek,
            obje({'kategoriler': {'type': 'array', 'items': METIN}}))
    k = [x.strip() for x in j['kategoriler'] if x.strip() and x.strip() not in ('Diğer', 'Mizah')]
    return list(dict.fromkeys(k)) + ['Diğer', 'Mizah']


def siniflandir(grup, kat):
    sistem = ('Bir kişinin Instagram kaydedilenlerini analiz ediyorsun.\nKategoriler (numara: ad):\n'
              + '\n'.join(f'{i}: {k}' for i, k in enumerate(kat, 1)) + '\n\n' + RUBRIK +
              '\n\nHer gönderi için: c = kod (aynen), k = kategori numarası, p = önem puanı, '
              'o = içeriği anlatan 1–2 cümlelik Türkçe özet ("bu video" diye başlama; somut bilgi varsa onu yaz), '
              'g = en fazla 8 kelimelik gerekçe. Açıklaması boş ya da belirsiz olanlara düşük puan ver ve özette bunu belirt. '
              'Mizah kategorisinin puanı her zaman 1. Alanlar: t=tür, u=kullanıcı, a=açıklama, s=transkript, g=görsel açıklaması, k=koleksiyon.')
    j = sor(sistem, '\n'.join(json.dumps(r, ensure_ascii=False) for r in grup),
            obje({'sonuc': {'type': 'array', 'items': obje({'c': METIN, 'k': {'type': 'integer'}, 'p': {'type': 'integer'}, 'o': METIN, 'g': METIN})}}))
    kodlar, satirlar, temiz = {r['c'] for r in grup}, {}, lambda s: ' '.join(str(s).split())  # TSV'de sekme/satır sonu olmasın
    for x in j['sonuc']:
        if x['c'] in kodlar and 1 <= x['k'] <= len(kat) and 1 <= x['p'] <= 5:
            p = 1 if kat[x['k'] - 1] == 'Mizah' else x['p']
            satirlar[x['c']] = '\t'.join([x['c'], str(x['k']), str(p), temiz(x['o']), temiz(x['g'])])
    (D / 'analiz').mkdir(exist_ok=True)
    no = max([int(f.stem) for f in (D / 'analiz').glob('*.tsv') if f.stem.isdigit()], default=0) + 1
    (D / 'analiz' / f'{no:03}.tsv').write_text('\n'.join(satirlar.values()) + '\n', encoding='utf-8')
    return len(satirlar)


def konu_ozeti(ad, ozetler):
    j = sor('Bir kişinin Instagram kaydedilenlerini özetliyorsun.',
            f'"{ad}" konusundaki kayıtların özetleri, önem puanıyla (yüksekten düşüğe):\n'
            + '\n'.join(f'[{p}] {o}' for p, o in ozetler) +
            '\n\nBu konuda neler kaydedildiğini anlatan tek paragraf yaz (4–6 cümle, Türkçe, düz yazı, liste yok). '
            'Öne çıkan somut başlıkları ve kaynakları say; zayıf ya da reklam içeriklerini bir cümleyle geç.',
            obje({'ozet': METIN}))
    return j['ozet']


def main():
    global client
    if not (D / 'saved.json').exists():
        sys.exit('data/saved.json yok: önce kaydedilenleri çek (README → 1. adım).')
    A = json.loads(AF.read_text(encoding='utf-8')) if AF.exists() else {}
    bekleyen = bekleyenler()
    eksik_ozet = [k for k in A.get('kategoriler', []) if k not in A.get('konu_ozetleri', {})]
    if not bekleyen and not eksik_ozet:
        return print('Analiz güncel.')
    tahmin = len(bekleyen) * (350 * FIYAT[0] + 150 * FIYAT[1]) / 1e6 + 0.3
    print(f'\n{len(bekleyen)} gönderi analiz bekliyor. Claude API ({MODEL}) ile tahmini maliyet ≈ ${tahmin:.1f}.')
    if not os.environ.get('ANTHROPIC_API_KEY'):
        anahtar = getpass.getpass('Claude API anahtarını yapıştır (görünmez; boş bırakırsan analiz atlanır): ').strip()
        if not anahtar:
            return print('Analiz atlandı. Claude Code, ChatGPT, Gemini gibi bir asistanla yapmak için: PROMPTLAR.md')
        os.environ['ANTHROPIC_API_KEY'] = anahtar
    elif input('Devam edilsin mi? [E/h] ').strip().lower().startswith('h'):
        return
    client = anthropic.Anthropic(max_retries=6)
    try:
        if 'kategoriler' not in A:
            A['kategoriler'] = kategori_oner(bekleyen)
            kaydet(A)
            print('\nÖnerilen konular:', ', '.join(A['kategoriler']))
            if input('Enter = bunlarla devam · d = düzenle (data/analysis.json açılır): ').strip().lower() == 'd':
                subprocess.run(['notepad', str(AF)]) if os.name == 'nt' else input(f'{AF} dosyasını düzenleyip Enter\'a bas.')
                A = json.loads(AF.read_text(encoding='utf-8'))
        kat, yeni = A['kategoriler'], 0
        for tur in range(3):  # model bir gönderiyi atlarsa sonraki turda tekrar sorulur
            for i in range(0, len(bekleyen), GRUP):
                yeni += siniflandir(bekleyen[i:i + GRUP], kat)
                print(f'  {min(i + GRUP, len(bekleyen))}/{len(bekleyen)} analiz edildi', flush=True)
            if not (bekleyen := bekleyenler()) or tur == 2:
                break
        an = analizler()
        for ad in (kat if yeni else eksik_ozet):
            ozetler = sorted(((p, o) for k, p, o in an.values() if kat[k - 1] == ad), reverse=True)[:150]
            if ozetler:
                A.setdefault('konu_ozetleri', {})[ad] = konu_ozeti(ad, ozetler)
                kaydet(A)
                print(f'  konu özeti: {ad}', flush=True)
    except anthropic.AuthenticationError:
        sys.exit('API anahtarı geçersiz.')
    except (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.APIStatusError, RuntimeError) as e:
        sys.exit(f'Analiz yarıda kaldı ({e}). Tekrar çalıştırınca kaldığı yerden devam eder.')
    finally:
        if harcama[0]:
            print(f'Harcanan: {harcama[0]:,} girdi + {harcama[1]:,} çıktı token ≈ ${(harcama[0] * FIYAT[0] + harcama[1] * FIYAT[1]) / 1e6:.2f}')


if __name__ == '__main__':
    main()
