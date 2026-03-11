// Configuración del Service Worker para Innexia BMC
window.SW_CONFIG = {
  // Configuración de cache
  cache: {
    // Tiempo de vida del cache en días
    maxAge: 7,
    // Tamaño máximo del cache en MB
    maxSize: 100,
    // Estrategias de cache por tipo de recurso
    strategies: {
      static: 'cache-first',
      api: 'network-first',
      images: 'cache-first',
      fonts: 'cache-first'
    }
  },
  
  // Configuración de sincronización offline
  sync: {
    // Tiempo máximo de retención de datos offline (horas)
    maxRetention: 24,
    // Intervalo de reintento de sincronización (minutos)
    retryInterval: 5,
    // Número máximo de reintentos
    maxRetries: 3
  },
  
  // Configuración de notificaciones
  notifications: {
    // Mostrar notificaciones de sincronización
    showSyncNotifications: true,
    // Mostrar notificaciones de estado offline
    showOfflineNotifications: true,
    // Sonido para notificaciones
    sound: true,
    // Vibración para notificaciones
    vibration: true
  },
  
  // Configuración de debugging
  debug: {
    // Logs detallados del service worker
    verbose: false,
    // Mostrar información de cache en consola
    showCacheInfo: false,
    // Simular modo offline para testing
    simulateOffline: false
  },
  
  // URLs de la API
  api: {
    baseUrl: 'http://localhost:8000', // Configuración estática para el service worker
    endpoints: {
      projects: '/api/projects',
      canvas: '/api/business-model-canvas',
      documents: '/api/documents',
      users: '/api/users'
    }
  },
  
  // Recursos críticos que siempre deben estar en cache
  criticalResources: [
    '/',
    '/index.html',
    '/manifest.json',
    '/src/main.tsx',
    '/src/App.css',
    '/src/index.css'
  ],
  
  // Patrones de recursos para cache automático
  cachePatterns: {
    // Assets estáticos
    static: [
      '/src/**/*.css',
      '/src/**/*.js',
      '/src/**/*.tsx',
      '/assets/**/*',
      '*.svg',
      '*.png',
      '*.jpg',
      '*.ico'
    ],
    // APIs
    api: [
      '/api/**/*'
    ]
  }
};

// Función para actualizar configuración en tiempo de ejecución
window.updateSWConfig = (newConfig) => {
  window.SW_CONFIG = { ...window.SW_CONFIG, ...newConfig };
  
  // Notificar al service worker sobre el cambio de configuración
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({
      type: 'CONFIG_UPDATE',
      config: window.SW_CONFIG
    });
  }
};

// Función para obtener configuración
window.getSWConfig = () => {
  return window.SW_CONFIG;
};

// Función para habilitar/deshabilitar debugging
window.setSWDebug = (enabled) => {
  window.SW_CONFIG.debug.verbose = enabled;
  window.updateSWConfig(window.SW_CONFIG);
};

// Función para limpiar cache
window.clearSWCache = async () => {
  if ('caches' in window) {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('Cache del Service Worker limpiado');
  }
};

// Función para forzar sincronización
window.forceSWSync = async () => {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({
      type: 'FORCE_SYNC'
    });
    console.log('Sincronización forzada solicitada');
  }
};

console.log('🔧 Configuración del Service Worker cargada');
console.log('📱 PWA Innexia BMC configurada y lista');


