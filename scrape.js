// Instagram kaydedilenlerini çeker → saved.json (İndirilenler klasörüne iner).
// Kullanım: Chrome'da instagram.com'a giriş yap → F12 → Console → bu dosyanın tamamını yapıştır → Enter.
// (Chrome ilk seferde yapıştırmayı engellerse konsola "allow pasting" yazıp Enter'a bas.)
// Sekmeyi kapatma; ~1000 kayıt ≈ 2-3 dk. Hata ile durursa aynı kodu tekrar yapıştır, kaldığı yerden devam eder.
// Sadece okur, hiçbir şeyi değiştirmez. Hesap güvenliği için sayfalar 3-5 sn arayla, tek tek istenir.
window.igIndir = () => {
  const S = window.__ig;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify({ cekildi: new Date().toISOString(), koleksiyonlar: S.koleksiyonlar, items: S.items })], { type: 'application/json' }));
  a.download = 'saved.json';
  a.click();
};
(async () => {
  const H = { headers: { 'X-IG-App-ID': '936619743392459' }, credentials: 'include' };
  const S = (window.__ig ||= { items: [], next: '', done: false, err: null, koleksiyonlar: {} });
  if (S.running) return;
  if (location.hostname !== 'www.instagram.com') return console.log('[ig] Önce www.instagram.com sekmesini aç ve giriş yap.');
  S.running = true; S.err = null;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const get = async url => { try { const r = await fetch(url, H); return r.ok ? r.json() : { http: r.status } } catch (e) { return { http: String(e) } } };

  if (!Object.keys(S.koleksiyonlar).length) {
    const c = await get('/api/v1/collections/list/');
    for (const k of c.items || []) S.koleksiyonlar[k.collection_id] = k.collection_name;
  }
  // transkript için sadece ses: DASH manifest'teki ayrı ses dosyası (~0.4 MB/dk). Yoksa en küçük video (~13 MB/dk)
  const vid = m => {
    const u = m.video_dash_manifest && new DOMParser().parseFromString(m.video_dash_manifest, 'text/xml')
      .querySelector('Representation[mimeType^="audio"] BaseURL')?.textContent;
    return u || (m.video_versions?.length ? m.video_versions.reduce((a, b) => (a.width <= b.width ? a : b)).url : null);
  };
  const kayit = m => {
    const parca = m.carousel_media || [m];
    const tur = m.media_type === 8 ? 'Albüm' : m.media_type === 2 ? (m.product_type === 'clips' ? 'Reel' : 'Video') : 'Fotoğraf';
    return {
      code: m.code,
      url: `https://www.instagram.com/${tur === 'Reel' ? 'reel' : 'p'}/${m.code}/`,
      tur,
      kullanici: m.user?.username || '',
      altyazi: m.caption?.text || '',
      tarih: new Date(m.taken_at * 1000).toISOString().slice(0, 10),
      sure: m.video_duration || null,
      ses_urls: parca.map(vid).filter(Boolean),
      alt_text: parca.map(p => p.accessibility_caption).filter(Boolean).join(' | '),
      koleksiyon: (m.saved_collection_ids || []).map(id => S.koleksiyonlar[id] || id),
    };
  };

  let hata = 0;
  while (!S.done) {
    const j = await get('/api/v1/feed/saved/posts/' + (S.next ? '?max_id=' + encodeURIComponent(S.next) : ''));
    if (j.http) {
      if (j.http === 401 || j.http === 403) { S.err = 'giriş yapılmamış'; break }
      if (++hata > 2) { S.err = j.http; break }
      console.log('[ig] hata', j.http, '→ 5 dk bekleniyor (Instagram yavaşlatıyor olabilir)');
      await sleep(300000); continue;
    }
    hata = 0;
    for (const it of j.items || []) if (it.media) S.items.push(kayit(it.media));
    S.next = j.next_max_id;
    S.done = !j.more_available || !S.next;
    document.title = `⏳ ${S.items.length} çekildi — KAPATMA`;
    console.log(`[ig] ${S.items.length} kayıt çekildi…`);
    if (!S.done) await sleep(3000 + Math.random() * 2000); // hesap güvenliği: yavaş ve sıralı
  }
  S.running = false;
  document.title = S.done ? `✓ ${S.items.length} çekildi` : `✗ hata ${S.err}`;
  if (S.done) { igIndir(); console.log(`[ig] Bitti: ${S.items.length} kayıt → saved.json indirildi. Şimdi baslat.bat'ı çalıştır.`) }
  else console.log(`[ig] Durdu (${S.err}). Kodu tekrar yapıştırırsan kaldığı yerden devam eder; o ana kadarkini indirmek için: igIndir()`);
})();
