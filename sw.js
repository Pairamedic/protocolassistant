const CACHE = 'pat-v8';

// Assets that rarely change — pre-cached, served cache-first
const ASSETS = [
  './star-of-life.svg',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './supervisor-icon-180.png',
  './supervisor-icon-192.png',
  './supervisor-icon-512.png',
  './pulse-icon.svg',
  './pulse-icon-180.png',
  './pulse-icon-192.png',
  './pulse-icon-512.png',
];

// Firebase CDN scripts — versioned URLs, safe to cache forever
const CDN = [
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore-compat.js',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c =>
      Promise.all([
        c.addAll(ASSETS),
        ...CDN.map(url =>
          fetch(url, { mode: 'no-cors' })
            .then(r => c.put(url, r))
            .catch(() => {})
        ),
      ])
    ).then(() => self.skipWaiting())
  );
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

  // Firebase Auth/Firestore API calls — never cache
  if (url.includes('googleapis.com') || url.includes('firebaseio.com') ||
      url.includes('identitytoolkit') || url.includes('securetoken')) return;

  // Firebase CDN scripts — cache-first (immutable versioned URLs)
  if (url.includes('gstatic.com/firebasejs')) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request, { mode: 'no-cors' }).then(resp => {
          caches.open(CACHE).then(c => c.put(e.request, resp.clone()));
          return resp;
        });
      })
    );
    return;
  }

  // HTML + manifest — network-first so updates are always picked up immediately.
  // Falls back to cache only when offline.
  if (url.startsWith(self.location.origin)) {
    const isHtmlOrManifest = /\.(html|json)(\?|$)/.test(url) || url === self.location.origin + '/';
    if (isHtmlOrManifest) {
      e.respondWith(
        fetch(e.request).then(resp => {
          if (resp.ok && e.request.method === 'GET') {
            caches.open(CACHE).then(c => c.put(e.request, resp.clone()));
          }
          return resp;
        }).catch(() => caches.match(e.request))
      );
      return;
    }

    // Static assets — cache-first, update in background
    e.respondWith(
      caches.open(CACHE).then(c =>
        c.match(e.request).then(cached => {
          const networkFetch = fetch(e.request).then(resp => {
            if (resp.ok && e.request.method === 'GET') c.put(e.request, resp.clone());
            return resp;
          }).catch(() => cached);
          return cached || networkFetch;
        })
      )
    );
  }
});
