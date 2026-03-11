const CACHE_NAME = 'innexia-bmc-v3';
const STATIC_CACHE = 'innexia-static-v3';
const DYNAMIC_CACHE = 'innexia-dynamic-v3';

// Archivos estáticos que se cachean inmediatamente
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/vite.svg',
  '/src/main.tsx',
  '/src/App.css',
  '/src/index.css'
];

// Estrategia de cache: Network First para API, Cache First para assets estáticos
const CACHE_STRATEGIES = {
  STATIC: 'cache-first',
  API: 'network-first',
  IMAGES: 'cache-first'
};

// Install event - Cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      caches.open(DYNAMIC_CACHE).then((cache) => {
        console.log('Dynamic cache ready');
        return cache;
      })
    ])
  );
  self.skipWaiting();
});

// Activate event - Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - Main caching strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // TEMPORALMENTE DESHABILITADO: Interceptación de todas las peticiones para resolver problemas de CORS
  // Skip non-GET requests
  // if (request.method !== 'GET') {
  //   return;
  // }

  // Handle different types of requests
  // TEMPORALMENTE DESHABILITADO: Interceptación de API para resolver problemas de autenticación
  // if (url.pathname.startsWith('/api/')) {
  //   // API requests - Network First strategy
  //   event.respondWith(handleApiRequest(request));
  // } else 
  // if (isStaticAsset(request)) {
  //   // Static assets - Cache First strategy
  //   event.respondWith(handleStaticAsset(request));
  // } else {
  //   // Other requests - Network First strategy
  //   event.respondWith(handleNetworkFirst(request));
  // }
  
  // TEMPORALMENTE: No interceptar ninguna petición
  return;
});

// Handle API requests with Network First strategy
async function handleApiRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for specific endpoints
    if (request.url.includes('/api/projects') || request.url.includes('/api/business-model-canvas')) {
      return new Response(JSON.stringify({ offline: true, message: 'Modo offline activo' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Generic offline response
    return new Response('Modo offline', { status: 503 });
  }
}

// Handle static assets with Cache First strategy
async function handleStaticAsset(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.log('Failed to fetch static asset:', error);
    return new Response('Asset no disponible offline', { status: 404 });
  }
}

// Handle other requests with Network First strategy
async function handleNetworkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(DYNAMIC_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response('Contenido no disponible offline', { status: 503 });
  }
}

// Check if request is for a static asset
function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    url.pathname.startsWith('/src/') ||
    url.pathname.startsWith('/assets/') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.tsx') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.jpg') ||
    url.pathname.endsWith('.ico')
  );
}

// Background sync for offline data
self.addEventListener('sync', (event) => {
  console.log('Background sync triggered:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(syncOfflineData());
  }
});

// Sync offline data when connection is restored
async function syncOfflineData() {
  try {
    // Get all clients
    const clients = await self.clients.matchAll();
    
    // Notify clients that sync is happening
    clients.forEach((client) => {
      client.postMessage({
        type: 'SYNC_STARTED',
        message: 'Sincronizando datos offline...'
      });
    });
    
    // Here you would implement the actual sync logic
    // For now, we'll just notify completion
    setTimeout(() => {
      clients.forEach((client) => {
        client.postMessage({
          type: 'SYNC_COMPLETED',
          message: 'Sincronización completada'
        });
      });
    }, 2000);
    
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Handle push notifications
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Nueva notificación de Innexia BMC',
    icon: '/vite.svg',
    badge: '/vite.svg',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver proyecto',
        icon: '/vite.svg'
      },
      {
        action: 'close',
        title: 'Cerrar',
        icon: '/vite.svg'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Innexia BMC', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/projects')
    );
  } else if (event.action === 'close') {
    // Just close the notification
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

