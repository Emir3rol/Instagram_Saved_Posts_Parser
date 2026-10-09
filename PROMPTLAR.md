# Yapay zekâ promptları (Claude, ChatGPT, Gemini, Codex, Cursor)

`baslat.bat` her şeyi Claude API ile kendisi yapar. Bu promptlar aynı işleri **API anahtarı olmadan, kullandığın yapay zekâ aboneliğiyle** yaptırmak ya da sonuçları düzeltmek için. Olduğu gibi kopyalayıp yapıştır.

| Araç | Ne için | Nasıl |
|---|---|---|
| **Claude Code**, **Codex CLI**, **Cursor**, **Gemini CLI** | 2. Analiz, 3. Düzeltme | Proje klasöründe aç, promptu yapıştır. Kuralları `AGENTS.md`'den okur, dosyaları kendisi yazar. |
| **ChatGPT**, **Gemini**, **Claude.ai** (web) | 2b. Analiz | Dosyayı sohbete yükle, promptu ver, verdiği dosyaları `data/` klasörüne koy. |
| **Claude in Chrome** | 1. Çekme | Tarayıcı eklentisi; konsola yapıştırmak istemeyenler için. |

---

## 1. Kaydedilenleri çekmek (Claude in Chrome)

> Konsola yapıştırmak istemiyorsan. Claude Code + Chrome eklentisiyle kullanıyorsan `scrape.js`'i kendisi okur; claude.ai'da kullanıyorsan `scrape.js`'in tamamını promptun sonuna yapıştır.

```text
Instagram kaydedilenlerimin tamamını çekmeni istiyorum. Chrome'da Instagram hesabım açık.

1. Yeni bir sekmede https://www.instagram.com/ aç. Giriş yapılı değilse dur ve bana söyle; şifre girme.
2. scrape.js'in içeriğini (bu klasördeki dosya ya da aşağıya yapıştırdığım kod) o sekmede JavaScript olarak çalıştır.
   Kod arka planda sayfa sayfa çeker; kendi istek döngünü yazma, yalnız bu kodu kullan
   (sayfalar arasında 3–5 sn bekler, hesabı korur).
3. İlerlemeyi window.__ig.items.length, bitişi window.__ig.done, hatayı window.__ig.err ile izle.
   Her kontrolde en fazla 30 sn bekle. Bana arada kaç kayıt çekildiğini söyle.
4. Sekmeyi kapatma, yenileme, başka sayfaya gitme.
5. Bitince saved.json kendiliğinden iner; inmezse sekmede igIndir() çalıştır.
6. window.__ig.err doluysa 5 dk bekle ve aynı kodu aynı sekmede tekrar çalıştır (kaldığı yerden devam eder).
   3 denemede düzelmezse dur, o ana kadarkini igIndir() ile indir ve bana söyle.

Kurallar: yalnız okuma. Instagram'da hiçbir şeye tıklama, beğenme, kayıt kaldırma, mesaj atma.
```

Bittiğinde `baslat.bat`'ı çalıştır; İndirilenler'deki `saved.json`'ı kendisi alır.

---

## 2. Analiz (Claude Code, Codex, Cursor, Gemini CLI — API anahtarı olmadan)

> `baslat.bat` analiz için anahtar sorduğunda boş bırak, sonra bunu kullan. Uzun sürer (1000 gönderi ≈ 20 grup); bağlam dolarsa yeni oturumda aynı promptu yapıştır, kaldığı yerden devam eder.

```text
Bu klasördeki Instagram kaydedilenlerimi analiz edeceksin. Önce AGENTS.md'yi oku.

1. `python build.py --compact` çalıştır (Windows'ta .venv\Scripts\python, PYTHONUTF8=1).
   data/compact.jsonl'e yalnız analiz bekleyen gönderiler yazılır. Alanlar:
   c=kod, t=tür, u=kullanıcı, a=açıklama, s=transkript, g=Instagram'ın görsel açıklaması, k=koleksiyon.
2. data/analysis.json yoksa ya da içinde "kategoriler" yoksa: compact.jsonl'den yaklaşık 300 satıra bakıp
   ilgi alanlarımı yansıtan 8–13 kısa Türkçe kategori öner (ör. "Yemek & Tarif"), sonuna "Diğer" ve "Mizah" ekle.
   Listeyi bana SOR, onayladığım haliyle {"kategoriler": [...]} olarak data/analysis.json'a yaz.
   Sıra = kategori numarası (1'den); sonradan yalnız sona ekleme yapılır.
3. compact.jsonl'u 50 satırlık parçalar halinde oku (tamamını tek seferde okuma). Her parça için
   data/analiz/NNN.tsv yaz (NNN sıradaki boş numara: 001, 002…). Her gönderi bir satır, sekmeyle ayrılmış:
   kod	kategori_no	puan	özet	gerekçe
   - Önem puanı 1–5 (özenle; yalnız açıklamaya değil, varsa transkripte göre):
     5 somut, uygulanabilir, kalıcı bilgi/teknik (adım adım öğretici, araç, yöntem)
     4 faydalı ama daha genel bilgi, iyi kaynak önerisi (kitap/film/araç listesi)
     3 ilham, referans, haber, ilginç bilgi
     2 zayıf içerik (reklam, klişe motivasyon, içeriği belirsiz)
     1 Mizah (meme, şaka, hayvan videoları, eğlence) — Mizah'ın puanı her zaman 1
   - özet: içeriği anlatan 1–2 Türkçe cümle ("bu video" diye başlama, somut bilgi varsa onu yaz).
   - gerekçe: en fazla 8 kelime. Özet ve gerekçede sekme ya da satır sonu olmasın.
   - Açıklaması ve transkripti boş ya da belirsiz olanlara düşük puan ver, özette bunu belirt.
4. Her 5 parçada bir kaç gönderi kaldığını söyle.
5. Hepsi bitince her kategori için yüksek puanlılardan başlayarak 4–6 cümlelik Türkçe konu özeti yaz;
   data/analysis.json'a "konu_ozetleri": {"Kategori adı": "paragraf", ...} olarak ekle.
6. `python build.py` ile raporu üret, kategorilere göre dağılımı ve 5 puanlıların sayısını bana söyle.
```

---

## 2b. Analiz (ChatGPT, Gemini ya da Claude.ai web sohbeti)

> Kodlama asistanı kullanmıyorsan. Önce `baslat.bat`'ı bir kez çalıştır (anahtarı boş bırak); `data/compact.jsonl` oluşur. Bu dosyayı sohbete yükle ve promptu ver. Uzun listelerde parça parça ilerler; her parçadan sonra "devam" yaz.

```text
Ekteki compact.jsonl Instagram'da kaydettiğim gönderiler; her satır bir gönderi:
c=kod, t=tür, u=kullanıcı, a=açıklama, s=transkript, g=görsel açıklaması, k=koleksiyon.

1. Önce yaklaşık 300 satıra bakıp ilgi alanlarımı yansıtan 8–13 kısa Türkçe kategori öner, sonuna "Diğer" ve
   "Mizah" ekle. Listeyi bana sor; onaylarsam sırayı sabit tut (1'den numaralı).
2. Sonra gönderileri sırayla, her mesajda 100'er tane analiz et. Her gönderi için şu sekmeyle ayrılmış satırı üret:
   kod	kategori_no	puan	özet	gerekçe
   - Önem puanı 1–5: 5 somut, uygulanabilir bilgi/teknik · 4 faydalı genel bilgi, kaynak önerisi ·
     3 ilham, haber, ilginç bilgi · 2 zayıf, reklam, belirsiz · 1 Mizah (meme, şaka, hayvan videosu). Mizah hep 1.
   - özet: içeriği anlatan 1–2 Türkçe cümle; gerekçe: en fazla 8 kelime. İkisinde de sekme ya da satır sonu olmasın.
   - Açıklaması ve transkripti boş olanlara düşük puan ver, özette "bilgi yok" de.
   Her 100'lükten sonra durup "devam" yazmamı bekle.
3. Hepsi bitince tüm satırları tek bir analiz.tsv dosyası olarak indirilebilir ver.
4. Her kategori için 4–6 cümlelik Türkçe konu özeti yaz ve şu biçimde analysis.json dosyası olarak ver:
   {"kategoriler": ["…", "Diğer", "Mizah"], "konu_ozetleri": {"Kategori adı": "paragraf", …}}
```

İnen dosyaları koy: `analiz.tsv` → `data/analiz/001.tsv`, `analysis.json` → `data/analysis.json`. Sonra `baslat.bat`. Sonradan yeni gönderi analiz ettirirsen yeni dosyayı `002.tsv`, `003.tsv`… diye kaydet ve aynı kategori listesini prompta ekle.

---

## 3. Konuları düzeltmek (Claude Code, Codex, Cursor, Gemini CLI)

> Örnek: "Diğer"de çoğunlukla kamp videoları varsa. Açıklaması olmayan videoları kapak görsellerinden anlar; `baslat.bat` açıkken kapaklar `data/thumbs/` klasöründe birikir.

```text
data/analiz/*.tsv'de "Diğer" kategorisindeki gönderileri (kategori numarası data/analysis.json sırasından)
özetleriyle listele. Bunların çoğu aslında kamp ve doğa videoları.

1. Önce data/analiz klasörünü ve data/analysis.json'u yedekle.
2. Özeti belirsiz ya da "bilgi yok" olanların kapak görsellerine bak (data/thumbs/KOD.jpg;
   yoksa baslat.bat açıkken http://127.0.0.1:8765/t/KOD adresini indir).
3. data/analysis.json'da "kategoriler" listesinin SONUNA "Kamp & Doğa" ekle (araya ekleme: numaralar kayar).
4. Kamp/doğa olanların satırlarında kategori numarasını yeni numarayla değiştir; kapaktan içeriği anlaşılanların
   özetini ve puanını da düzelt. Başka kategoriye ait olduğu belli olanları (ör. gitar videosu) doğru yere taşı.
5. "Kamp & Doğa" için konu özeti yaz, "Diğer"in özetini kalanlara göre güncelle.
6. Neyi nereye taşıdığını tablo olarak göster, sonra `python build.py` çalıştır.
```

"Diğer" ve "Kamp & Doğa" yerine kendi durumuna uyan kategori adlarını yaz.
