// NEOTRIS 오프라인 캐시 (cache-first)
const CACHE = 'neotris-v5';   // 버전을 올리면 옛 캐시가 activate 때 전부 삭제됨
const ASSETS = ['./', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const put = res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return res; };
  if (e.request.mode === 'navigate') {
    // HTML은 network-first + no-cache: 브라우저 HTTP 캐시(10분)를 건너뛰고 서버에 재확인.
    // 오프라인일 때만 캐시 사용.
    e.respondWith(fetch(e.request, { cache: 'no-cache' }).then(put).catch(() => caches.match(e.request)));
  } else {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(put)));
  }
});
