**Türkçe** · [English](README.en.md)

# Kaydedilenler: Instagram kaydedilenlerini Claude ve ChatGPT ile düzenle

![Claude](https://img.shields.io/badge/Claude-API%20%C2%B7%20Code%20%C2%B7%20Chrome-D97757?logo=anthropic&logoColor=white)
![ChatGPT](https://img.shields.io/badge/ChatGPT%20%2F%20GPT-haz%C4%B1r%20promptlar-10A37F?logo=openai&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini%20%C2%B7%20Codex%20%C2%B7%20Cursor-AGENTS.md-4285F4)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-tek%20tu%C5%9F%20kurulum-0078D6)

Instagram'da kaydettiğin her şeyi çeker, yapay zekâ ile (Claude ya da ChatGPT) konulara ayırır, her birine kısa özet yazar ve önem sırasına dizer. Sonra Reels gibi kaydırarak izler, **sağa atıp tutar, sola atıp ayıklarsın**. Her şey kendi bilgisayarında çalışır.

> **EN:** Export your Instagram saved posts, let AI (Claude API, Claude Code, ChatGPT/GPT, Gemini, Codex, Cursor) sort them into topics with summaries and importance scores, then review them Reels-style and swipe right to keep / left to trash. Runs locally, one-click Windows setup. → [English README](README.en.md)

![Ana sayfa: konular ve filtreler](docs/ana-sayfa.jpg)

| Konuya ve öneme göre süzülmüş liste | İzleme ve ayıklama |
|---|---|
| ![Filtreli liste](docs/liste.jpg) | ![İzleme ekranı](docs/izleme.jpg) |

## Neler var

- **Konular**: Kaydettiklerin 10–15 konuya ayrılır; her konunun özeti ve Instagram koleksiyonu gibi mozaik kapağı olur.
- **Önem sırası**: Her gönderiye 1–5 puan ve 1–2 cümlelik özet. Liste "Mutlaka bak"tan "Mizah"a doğru dizilir.
- **Filtreler**: Arama, önem, tür (Reel / Fotoğraf / Albüm / Video), konu ve durum. Sayılar seçtiğin filtreye göre değişir.
- **İzleme**: Reels gibi dikey akış, video kendiliğinden oynar.
  - Sağa sürükle (ya da → tuşu): gönderi kalır.
  - Sola sürükle (ya da ← tuşu): gönderi **çöp kutusuna** gider.
  - Her karardan sonra birkaç saniye "Geri al" çıkar.
- **Çöp kutusu**: Ayıkladıkların silinmez, ayrı bir yerde durur. İstediğin zaman geri alabilirsin.
- Koyu ve açık tema, telefon uyumlu. Filtreli görünümler adres çubuğundan yer imi olarak saklanabilir: `#konu=…&onem=4&izle`.

## Kurulum (Windows, tek tuş)

1. Bu sayfada **Code → Download ZIP**'e tıkla, bir klasöre çıkar. Git kullanıyorsan `git clone` da olur.
2. **`baslat.bat`**'a çift tıkla. Python yoksa kendisi kurar, gerekenleri indirir, ekranda adım adım ne yapacağını söyler:

   | Adım | Ne olur |
   |---|---|
   | **1. Çek** | Instagram açılır, çekme kodu panoya kopyalanır. **F12 → Console → Ctrl+V → Enter**. ~1000 kayıt 2–3 dakika sürer. Bitince `saved.json` iner. |
   | **2. Analiz** | `baslat.bat`'ı tekrar çalıştır. İndirilen dosyayı kendisi alır ve [Claude API anahtarını](https://console.anthropic.com/settings/keys) sorar. Konuları önerir, onayından sonra hepsini analiz eder. |
   | **3. İzle** | Rapor tarayıcıda açılır. Siyah pencere açık kaldıkça çalışır. |

Sonraki seferlerde de yalnız `baslat.bat` yeter. Yeni kaydettiklerini çekmek istersen 1. adımı tekrarla; yalnız yeni gönderiler analiz edilir.

**Maliyet:** Analiz Claude Opus 5.5 ile yapılır. 1000 gönderi yaklaşık **4–5 $** tutar ve bir kez ödenir. Başlamadan tahmini tutarı gösterir, sonunda harcananı yazar.

**API anahtarın yoksa:** Analizi kullandığın yapay zekâ aboneliğiyle yaptırabilirsin (aşağıdaki tablo). Anahtarı boş bırakırsan rapor yine açılır, analiz eklenince konular ve özetler gelir.

## Hangi yapay zekâ ile?

| Kullandığın | Kaydedilenleri çekme | Analiz (konu, puan, özet) |
|---|---|---|
| **Claude API** anahtarı | konsol kodu (`baslat.bat` açar) | **otomatik**: `baslat.bat` anahtarı sorar, gerisini yapar |
| **Claude Code**, **Codex CLI**, **Cursor**, **Gemini CLI** | konsol kodu | proje klasöründe [hazır prompt](PROMPTLAR.md); kuralları `AGENTS.md`'den okur |
| **ChatGPT**, **Gemini**, **Claude.ai** (web) | konsol kodu | `compact.jsonl`'u sohbete yükle, [hazır prompt](PROMPTLAR.md) ile analiz dosyalarını al |
| **Claude in Chrome** | [hazır prompt](PROMPTLAR.md) ile Claude çeker | yukarıdakilerden biri |

Kaydedilenleri çekmek için hiçbir yapay zekâ gerekmez: `baslat.bat` kodu panoya kopyalar, sen tarayıcı konsoluna yapıştırırsın.

<details>
<summary>macOS / Linux</summary>

`saved.json`'ı `data/` klasörüne kendin koy, sonra:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python analiz.py && .venv/bin/python build.py && .venv/bin/python izle.py
```
</details>

## İsteğe bağlı: videoların sesini yazıya dökmek

Özetler normalde gönderi açıklamasından çıkarılır. Konuşmalı eğitim videolarında ses dökümü daha iyi özet ve puan verir. NVIDIA ekran kartı önerilir.

```bat
.venv\Scripts\pip install -r requirements-transkript.txt
.venv\Scripts\python transcribe.py
```

Ekran kartın yoksa `transcribe.py --device cpu --model small` ile çalıştır. Kaydedilenleri çektikten hemen sonra çalıştır, çünkü ses bağlantıları yaklaşık bir gün geçerli. Ardından `baslat.bat`.

## Hazır promptlar

[PROMPTLAR.md](PROMPTLAR.md) dört hazır prompt içerir:

- Kaydedilenleri **Claude in Chrome** ile çekmek.
- Analizi **Claude Code / Codex / Cursor / Gemini CLI** ile yaptırmak (API anahtarı olmadan).
- Analizi **ChatGPT / Gemini / Claude.ai** web sohbetinde yaptırmak.
- Konuları sonradan **düzeltmek**. Örneğin "Diğer"deki kamp videolarını kapak görsellerine bakarak yeni bir konuya taşımak.

## Kendi sunucunda (isteğe bağlı)

Telefondan ya da her yerden açmak için [`sunucu/`](sunucu) klasöründe Docker ve anahtarlı Caddy örneği var. Tut / çöp kutusu kararları sunucuda tutulur, böylece her cihazda aynı liste görünür.

## Gizlilik

- Kaydedilenlerin, analizler, kapaklar, kararların ve rapor yalnızca bilgisayarındaki `data/` klasöründe ve `rapor.html`'de durur. İkisi de `.gitignore`'da.
- Çekme kodu yalnızca okur, Instagram'da hiçbir şeyi değiştirmez. Sayfalar 3–5 saniye arayla istenir. Şifren ya da oturum bilgin hiçbir dosyaya yazılmaz.
- Çöp kutusu yalnızca bu listeyi etkiler, Instagram'daki kayıtların silinmez.
- Analiz için gönderi açıklamaları (varsa ses dökümleri de) seçtiğin yapay zekâya gönderilir: Claude API ya da kullandığın asistan.
- Instagram'ın resmî olmayan web adreslerini kullanır. Instagram bir şeyi değiştirirse çekme bozulabilir. Kendi hesabında, kendi sorumluluğunda kullan.

## Nasıl çalışır

| Dosya | Görev |
|---|---|
| `scrape.js` | instagram.com konsolunda çalışır, kaydedilenleri sayfa sayfa okur → `saved.json` |
| `analiz.py` | Claude API: konular, puan, özet → `data/analiz/*.tsv`, konu özetleri → `data/analysis.json` |
| `transcribe.py` | isteğe bağlı: video seslerini faster-whisper ile yazıya döker |
| `build.py` | hepsini tek dosyalık rapora döker → `rapor.html` |
| `izle.py` | raporu `127.0.0.1:8765`'te sunar; videoları ve kapakları Instagram'dan o an alır, kararları saklar |
| `baslat.bat` | hepsini sırayla çalıştırır |
| `AGENTS.md` | Claude Code, Codex, Cursor, Gemini CLI için proje kuralları ve veri biçimi |

Rapor ve yerel sunucu yalnızca Python standart kütüphanesiyle çalışır; tek ek paket `anthropic`.
