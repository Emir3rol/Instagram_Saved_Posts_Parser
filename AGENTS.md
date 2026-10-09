# Instagram Kaydedilenler — yapay zekâ asistanları için kurallar

Claude Code, Codex, Cursor, Gemini CLI ve benzeri kodlama asistanları bu dosyayı okur (Claude Code `CLAUDE.md` üzerinden).
Uygulama: kaydedilen Instagram gönderilerini çeker, konulara ayırır, önem sırasına dizer, Reels gibi izletip ayıklatır.
Kullanıcı rehberi: README.md. Hazır promptlar: PROMPTLAR.md.

| Dosya | Görev |
|---|---|
| `scrape.js` | instagram.com konsolunda çalışır → `saved.json` |
| `analiz.py` | Claude API ile kategori + puan + özet → `data/analiz/*.tsv`, `data/analysis.json` |
| `transcribe.py` | isteğe bağlı: video seslerini yazıya döker → `data/transcripts/` |
| `build.py` | hepsini tek dosyaya döker → `rapor.html` (`--compact`: analiz bekleyenler → `data/compact.jsonl`) |
| `izle.py` | raporu 127.0.0.1:8765'te sunar; video/kapak vekili, tut/çöp kutusu kararları (`data/kararlar.json`) |
| `baslat.bat` | Windows'ta hepsini sırayla çalıştırır |

## Veri biçimi (analizi elle ya da başka bir modelle yapıyorsan)

- Girdi `data/compact.jsonl`, satır başına bir gönderi: `c` kod, `t` tür, `u` kullanıcı, `a` açıklama, `s` transkript, `g` görsel açıklaması, `k` koleksiyon.
- `data/analysis.json`: `{"kategoriler": ["…", "Diğer", "Mizah"], "konu_ozetleri": {"kategori": "paragraf"}}`.
  `kategori_no` bu listenin sırasıdır (1'den); yeni kategori hep sona eklenir, sıra değişirse eski satırlar yanlış konuya düşer.
- `data/analiz/NNN.tsv`, satır başına: `kod⇥kategori_no⇥puan⇥özet⇥gerekçe`. Özet 1–2 Türkçe cümle, gerekçe ≤ 8 kelime; ikisinde de sekme ya da satır sonu olmaz.
- Önem puanı: 5 somut, uygulanabilir bilgi · 4 faydalı genel bilgi / kaynak · 3 ilham, haber, ilginç · 2 zayıf, reklam, belirsiz · 1 Mizah (Mizah hep 1).

## Kurallar

- `data/` ve `rapor.html` kişisel veri: depoya ekleme, hiçbir yere yükleme.
- Python: Windows'ta `.venv/Scripts/python`, Türkçe çıktı için `PYTHONUTF8=1`. Rapor ve sunucu yalnız standart kütüphane; tek paket `anthropic`.
- Instagram'a yalnız okuma amaçlı, yavaş ve sıralı istek. Kullanıcının oturum çerezi hiçbir dosyaya yazılmaz.
- `.bat` dosyaları CRLF satır sonuyla kalmalı (LF'de cmd Türkçe satırları kaydırarak okur).
