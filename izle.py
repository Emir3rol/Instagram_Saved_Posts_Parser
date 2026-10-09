"""rapor.html'i yerelde sunar; /v/<code> o anki video adresine yönlendirir (izleme akışında otomatik oynatma için).
Instagram'ın embed oynatıcısı dışarıdan başlatılamıyor, video adresleri de ~1,5 günde eskiyor; bu yüzden adres her açılışta embed sayfasından alınır.
/t/<code> kapak görseli: CDN başka siteye göstermeye izin vermiyor (CORP same-origin), bu yüzden buradan geçer ve data/thumbs'a bir kez kaydedilir.
Çalıştır: baslat.bat (ya da python izle.py). Sadece 127.0.0.1'e açılır; sunucuda (sunucu/compose.yml) HOST=0.0.0.0, önünde anahtarlı Caddy."""
import json, os, re, threading, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 8765
HOST = os.environ.get('HOST', '127.0.0.1')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
# Sec-Fetch başlıkları olmadan Instagram video adresi olmayan giriş sayfası döndürüyor
BASLIK = {'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'en-US,en;q=0.9',
          'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site'}
onbellek = {}
KAPAK = Path(__file__).with_name('data') / 'thumbs'
kilit = threading.Semaphore(4)  # sayfa kaydırılınca onlarca kapak birden istenir; Instagram'a aynı anda en fazla 4 istek
# izleme ekranındaki kaydırma kararları: {code: 'tut' | 'sil'}; 'sil' = çöp kutusu (Instagram'a dokunulmaz)
KARAR = Path(__file__).with_name('data') / 'kararlar.json'
kararlar = json.loads(KARAR.read_text(encoding='utf-8')) if KARAR.exists() else {}
karar_kilit = threading.Lock()


def karar_yaz(code, d):
    with karar_kilit:
        if d:
            kararlar[code] = d
        else:
            kararlar.pop(code, None)
        KARAR.parent.mkdir(exist_ok=True)
        gecici = KARAR.with_suffix('.tmp')
        gecici.write_text(json.dumps(kararlar, ensure_ascii=False), encoding='utf-8')
        os.replace(gecici, KARAR)  # yarım yazılmış dosya kalmasın


def kapak(code):
    f = KAPAK / f'{code}.jpg'
    if not f.exists():
        with kilit:
            if not f.exists():
                r = urllib.request.urlopen(urllib.request.Request(f'https://www.instagram.com/p/{code}/media/?size=m', headers={'User-Agent': UA}), timeout=20)
                if not r.headers.get_content_type().startswith('image/'):  # giriş sayfası vb. önbelleğe girmez
                    raise ValueError('görsel değil')
                KAPAK.mkdir(exist_ok=True)
                f.write_bytes(r.read())
    return f.read_bytes()


SAYFA = {**BASLIK, 'Accept': 'text/html,application/xhtml+xml', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Site': 'none'}


def ara(adres, baslik, desen):
    t = urllib.request.urlopen(urllib.request.Request(adres, headers=baslik), timeout=20).read().decode('utf-8', 'replace')
    m = re.search(desen, t)
    return m and re.sub(r'\\+/', '/', re.sub(r'\\+u0026', '&', m.group(1)))


def video_url(code):
    if code not in onbellek:
        # 1) embed sayfası hafif (~260 KB) ama telifli müzikli Reels'te adresi vermiyor (örnekte ~%28)
        #    JSON içinde JSON: \"video_url\":\"https:\\\/\\\/…\"
        u = ara(f'https://www.instagram.com/p/{code}/embed/', BASLIK, r'video_url[\\"]+:[\\"]+(https:.+?)\\*"')
        # 2) girişsiz gönderi sayfası (~830 KB): "video_versions":[{"type":101,"url":"https:\/\/…mp4?…"
        u = u or ara(f'https://www.instagram.com/p/{code}/', SAYFA, r'"video_versions":\[\{[^\]]*?"url":"(https:[^"]+)"')
        if not u:
            return None  # önbelleğe girmez: Instagram geçici engel koymuş olabilir, sonra yeniden denenir
        onbellek[code] = u
    return onbellek[code]


class Sunucu(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = self.path.split('?')[0]  # sunucuda ilk giriş /?k=<anahtar> ile gelir
        if self.path.startswith('/v/'):
            code = self.path[3:]
            if not re.fullmatch(r'[\w-]+', code):
                return self.send_error(400)
            try:
                u = video_url(code)
            except Exception:
                u = None
            if not u:
                return self.send_error(404)
            self.send_response(302)
            self.send_header('Location', u)
            self.end_headers()
        elif self.path.startswith('/t/'):
            code = self.path[3:]
            if not re.fullmatch(r'[\w-]+', code):
                return self.send_error(400)
            try:
                b = kapak(code)
            except Exception:
                return self.send_error(404)
            self.gonder(b, 'image/jpeg', 'max-age=31536000')
        elif self.path == '/kararlar':
            with karar_kilit:
                b = json.dumps(kararlar).encode()
            self.gonder(b, 'application/json', 'no-store')
        elif self.path in ('/', '/rapor.html'):
            self.gonder(Path(__file__).with_name('rapor.html').read_bytes(), 'text/html; charset=utf-8', 'no-cache')
        else:
            self.send_error(404)

    def do_POST(self):  # /karar  {"c": code, "d": "tut" | "sil" | ""}  ("" = kararı kaldır)
        if self.path.split('?')[0] != '/karar':
            return self.send_error(404)
        try:
            n = int(self.headers.get('Content-Length', 0))
            v = json.loads(self.rfile.read(n)) if 0 < n <= 200 else {}
            c, d = v['c'], v['d']
            if not (isinstance(c, str) and re.fullmatch(r'[\w-]{5,20}', c) and d in ('tut', 'sil', '')):
                raise ValueError
        except Exception:
            return self.send_error(400)
        karar_yaz(c, d)
        self.send_response(204)
        self.end_headers()

    def gonder(self, b, tur, cache):
        try:
            self.send_response(200)
            self.send_header('Content-Type', tur)
            self.send_header('Content-Length', str(len(b)))
            self.send_header('Cache-Control', cache)
            self.end_headers()
            self.wfile.write(b)
        except ConnectionError:  # tarayıcı kaydırırken yüklenmeyi iptal etti
            pass

    def log_message(self, *a):
        pass


class SessizSunucu(ThreadingHTTPServer):
    def handle_error(self, request, client_address):  # tarayıcı yüklemeyi yarıda kesince konsola hata dökmesin
        import sys
        if not isinstance(sys.exc_info()[1], ConnectionError):
            super().handle_error(request, client_address)


if __name__ == '__main__':
    s = SessizSunucu((HOST, PORT), Sunucu)
    print(f'Rapor: http://{HOST}:{PORT}/  (kapatmak için bu pencereyi kapat)', flush=True)
    if HOST == '127.0.0.1':
        webbrowser.open(f'http://127.0.0.1:{PORT}/')
    s.serve_forever()
