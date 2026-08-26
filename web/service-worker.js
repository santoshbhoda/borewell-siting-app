/**
 * BSMA GeoAI Borewell Siting App — Service Worker (v8.0.0)
 * Bulletproof local Leaflet DOM basemap streaming, Satellite-first & 100% offline caching.
 */

const CACHE_NAME = 'borewell-ai-v8.2.0';
const STATIC_ASSETS = [
  './',
  './index.html',
  './css/styles.css',
  './js/app.js',
  './vendor/leaflet/leaflet.js',
  './vendor/leaflet/leaflet.css',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './data/gwpi_grid.json',
  './data/catchment_gwpi_map.png',
  './data/farm_siting_plan.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[Service Worker v4] Pre-caching core app shell...');
      try {
        await cache.addAll(STATIC_ASSETS);
      } catch (err) {
        console.warn('[Service Worker v4] Partial cache on install:', err);
      }
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker v4] Purging old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // 1. Direct browser pass-through for Map Tiles & External APIs (prevents opaque tile blocking)
  if (
    url.origin.includes('tile.openstreetmap.org') ||
    url.origin.includes('cartocdn.com') ||
    url.origin.includes('arcgisonline.com') ||
    url.origin.includes('open-meteo.com')
  ) {
    return; // Native browser fetch
  }

  // 2. CDNs: Stale-while-revalidate
  if (url.origin.includes('unpkg.com') || url.origin.includes('fonts.') || url.origin.includes('cdnjs.')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cachedResponse = await cache.match(request);
        const fetchPromise = fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            cache.put(request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // 3. App Shell: Network-First with Cache Fallback
  event.respondWith(
    fetch(request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          if (request.mode === 'navigate') return caches.match('./index.html');
        });
      })
  );
});
