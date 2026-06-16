const CACHE = 'pat-v4';

// Local app files — always pre-cached
const LOCAL = [
  './index.html',
  './ProtocolAssistant.html',
  './supervisor.html',
  './narrative.html',
  './manifest.json',
  './star-of-life.svg',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
];

// Firebase CDN scripts — versioned URLs never change, safe to cache forever
const CDN = [
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js',
  'https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore-compat.js',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c =>
      // Cache local files with regular requests; CDN with no-cors
      Promise.all([
        c.addAll(LOCAL),
        ...CDN.map(url =>
          fetch(url, { mode: 'no-cors' })
            .then(r => c.put(url, r))
            .catch(() => {}) // best-effort — network may be unavailable at install
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

  // Firebase Auth/Firestore API calls — always pass through, never cache
  if (url.includes('googleapis.com') || url.includes('firebaseio.com') ||
      url.includes('identitytoolkit') || url.includes('securetoken')) return;

  // Firebase CDN scripts — cache-first (versioned, immutable)
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

  // Local app files — stale-while-revalidate
  // Serve from cache immediately; update cache in background when online
  if (url.startsWith(self.location.origin)) {
    e.respondWith(
      caches.open(CACHE).then(c =>
        c.match(e.request).then(cached => {
          const networkFetch = fetch(e.request).then(resp => {
            if (resp.ok && e.request.method === 'GET') c.put(e.request, resp.clone());
            return resp;
          }).catch(() => cached); // offline — return cached if network fails
          return cached || networkFetch;
        })
      )
    );
  }
});
