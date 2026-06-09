const CACHE = 'pat-v2';
const CORE = ['./ProtocolAssistant.html', './star-of-life.svg', './manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = e.request.url;
  // Let Firebase, gstatic, and cross-origin requests pass through unmodified
  if (!url.startsWith(self.location.origin) ||
      url.includes('firestore') || url.includes('firebase') || url.includes('gstatic')) return;
  e.respondWith(
    fetch(e.request).then(resp => {
      if (resp.ok && e.request.method === 'GET') {
        caches.open(CACHE).then(c => c.put(e.request, resp.clone()));
      }
      return resp;
    }).catch(() => caches.match(e.request))
  );
});
