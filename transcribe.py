"""Video/Reel seslerini (sadece ses akışı) yazıya çevirir: data/saved.json → data/transcripts/<code>.txt
Boş dosya = konuşma yok. İndirilemeyenler data/transkript_hatalari.txt'ye yazılır
(URL süresi dolduysa scrape.js'i yeniden çalıştır). Var olan transkriptler atlanır.
Kullanım: .venv/Scripts/python transcribe.py [--model large-v3-turbo] [--device cuda|cpu]"""
import argparse, glob, io, json, os, sys, urllib.request
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

for d in glob.glob(os.path.join(sys.prefix, 'Lib', 'site-packages', 'nvidia', '*', 'bin')):  # pip'le gelen CUDA DLL'leri
    os.add_dll_directory(d)
    os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
from faster_whisper import WhisperModel

p = argparse.ArgumentParser()
p.add_argument('--model', default='large-v3-turbo')
p.add_argument('--device', default='cuda')
a = p.parse_args()

out = Path('data/transcripts')
out.mkdir(parents=True, exist_ok=True)
items = [x for x in json.load(open('data/saved.json', encoding='utf-8'))['items']
         if x['ses_urls'] and not (out / f"{x['code']}.txt").exists()]
model = WhisperModel(a.model, device=a.device, compute_type='float16' if a.device == 'cuda' else 'int8')


def indir(x):  # sesler bellekte kalır, diske yazılmaz
    return [urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read()
            for u in x['ses_urls']]


# GPU indirmeyi beklemesin: sıradaki 16 öğe 8 iş parçacığıyla önceden indirilir
ex, q, kalan = ThreadPoolExecutor(8), deque(), iter(items)
def doldur():
    while len(q) < 16 and (x := next(kalan, None)):
        q.append((x, ex.submit(indir, x)))


hatalar, i = [], 0
doldur()
while q:
    x, fut = q.popleft()
    doldur()
    i += 1
    try:
        parts, dil = [], set()
        for b in fut.result():
            segs, info = model.transcribe(io.BytesIO(b), vad_filter=True)  # VAD: müzik/sessizlikte uydurma metni azaltır
            parts.append(' '.join(s.text.strip() for s in segs))
            dil.add(info.language)
        (out / f"{x['code']}.txt").write_text('\n'.join(parts).strip(), encoding='utf-8')
        print(f"{i}/{len(items)} {x['code']} {','.join(dil)}", flush=True)
    except Exception as e:
        hatalar.append(f"{x['code']}\t{e}")
        print(f"{i}/{len(items)} {x['code']} HATA {e}", flush=True)
Path('data/transkript_hatalari.txt').write_text('\n'.join(hatalar), encoding='utf-8')
print('bitti, hata:', len(hatalar))
