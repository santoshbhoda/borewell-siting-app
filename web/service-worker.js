/**
 * BSMA GeoAI Borewell Siting App — Service Worker (v3.0.0)
 * Real-time Dynamic Multi-Terrain Physics & Hydrogeological Siting Engine
 */

const CACHE_NAME = 'borewell-ai-v3.0.0';
const STATIC_ASSETS = [
  './',
  './index.html',
  './css/styles.css',
  './js/app.js',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './data/farm_siting_report.geojson',
  './data/mangofarm_siting_report.geojson',
  './data/gwpi_grid.json',
  './data/catchment_gwpi_map.png',
  './data/farm_siting_plan.png',
  './data/mangofarm_siting_plan.png',
  './data/Borewell_Siting_Full_Report.pdf',
  './data/Borewell_Siting_Full_Report_MangoFarm.pdf'
];

// External CDNs to cache on install
const EXTERNAL_ASSETS = [
  'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css',
  'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js',
  'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[Service Worker v2] Caching static assets & app shell...');
      try {
        await cache.addAll(STATIC_ASSETS);
      } catch (err) {
        console.warn('[Service Worker v2] Local asset caching partial:', err);
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
            console.log('[Service Worker v2] Removing old cache:', cache);
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

  // 1. Map Tiles & External CDNs: Stale-While-Revalidate with caching
  if (url.origin.includes('tile.openstreetmap.org') || url.origin.includes('unpkg.com') || url.origin.includes('fonts.') || url.origin.includes('cdnjs.')) {
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

  // 2. App Shell & Data: Network-First with Cache Fallback (Ensures fresh updates, falls back to cache if offline)
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
        // If network is offline, serve from cache
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          if (request.mode === 'navigate') {
            return caches.match('./index.html');
          }
        });
      })
  );
});
