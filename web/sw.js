const CACHE_NAME = "fp-bridge-v2";
const ASSETS = ["/", "/manifest.json", "/icon.svg"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  // API and WebSocket requests: network only
  if (e.request.url.includes("/status") ||
      e.request.url.includes("/power/") ||
      e.request.url.includes("/reset") ||
      e.request.url.includes("/ws")) {
    return;
  }
  // Static assets: cache first, fallback to network
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
