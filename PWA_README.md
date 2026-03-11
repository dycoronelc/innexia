# Innexia Business Model Canvas - PWA

## 🚀 Características PWA

### Funcionalidades Principales
- **Instalación como App**: Instálate en el escritorio o pantalla de inicio
- **Trabajo Offline**: Funcionalidad completa sin conexión a internet
- **Sincronización Automática**: Los datos se sincronizan cuando vuelves a estar online
- **Notificaciones Push**: Recibe actualizaciones importantes
- **Cache Inteligente**: Estrategias de cache optimizadas para diferentes tipos de contenido

### Tecnologías PWA Utilizadas
- **Service Worker**: Para cache offline y sincronización
- **Web App Manifest**: Para instalación y apariencia nativa
- **Cache API**: Para almacenamiento offline de recursos
- **Background Sync**: Para sincronización en segundo plano
- **Push API**: Para notificaciones push

## 📱 Instalación

### Para Usuarios
1. Abre la aplicación en Chrome/Edge
2. Aparecerá un banner de instalación
3. Haz clic en "Instalar" o usa el botón de instalación en la barra de direcciones
4. La app se instalará en tu escritorio/pantalla de inicio

### Para Desarrolladores
```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Construir para producción
npm run build

# Vista previa de producción
npm run preview
```

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env.local`:
```env
VITE_API_URL=http://localhost:8000
VITE_VAPID_PUBLIC_KEY=tu_clave_vapid_publica
```

### Service Worker
El service worker se registra automáticamente y maneja:
- Cache de recursos estáticos
- Cache de respuestas de API
- Sincronización offline
- Notificaciones push

## 📊 Funcionalidades Offline

### Business Model Canvas
- ✅ Crear y editar bloques del canvas
- ✅ Agregar/eliminar elementos
- ✅ Modificar propuestas de valor
- ✅ Cambios guardados localmente
- ✅ Sincronización automática al volver online

### Gestión de Proyectos
- ✅ Ver proyectos existentes (cache)
- ✅ Crear nuevos proyectos (cola offline)
- ✅ Editar proyectos (cola offline)
- ✅ Eliminar proyectos (cola offline)

### Documentos
- ✅ Subir documentos (cola offline)
- ✅ Ver documentos existentes (cache)
- ✅ Editar metadatos (cola offline)

## 🎯 Estrategias de Cache

### Cache First (Assets Estáticos)
- CSS, JS, imágenes
- Fuentes y iconos
- Archivos de configuración

### Network First (API)
- Endpoints de datos
- Respuestas de API
- Fallback a cache si falla la red

### Cache Only (Recursos Críticos)
- HTML principal
- Service Worker
- Manifest

## 🔄 Sincronización

### Cola Offline
Los cambios offline se almacenan en:
- `localStorage` para persistencia
- Cola de sincronización automática
- Reintentos automáticos en caso de error

### Tipos de Sincronización
1. **Automática**: Al volver a estar online
2. **Manual**: Botón de sincronización
3. **Background**: En segundo plano

## 📱 Notificaciones

### Tipos de Notificaciones
- **Instalación**: Confirmación de instalación exitosa
- **Sincronización**: Estado de sincronización offline
- **Push**: Notificaciones del servidor (configurable)

### Permisos
- Solicitud automática de permisos
- Manejo de estados de permiso
- Fallback para navegadores no compatibles

## 🧪 Testing

### Testing Offline
```bash
# Chrome DevTools
1. Abre DevTools (F12)
2. Ve a Application > Service Workers
3. Marca "Offline"
4. Prueba la funcionalidad offline

# Testing de Cache
1. Application > Storage > Cache Storage
2. Verifica que los recursos estén cacheados
3. Prueba la funcionalidad sin red
```

### Testing de Instalación
```bash
# Chrome DevTools
1. Application > Manifest
2. Verifica que el manifest sea válido
3. Prueba la instalación
```

## 🚀 Despliegue

### Requisitos de Producción
- **HTTPS**: Obligatorio para PWA
- **Service Worker**: Debe estar en la raíz del dominio
- **Manifest**: Accesible públicamente
- **Icons**: Múltiples tamaños disponibles

### Optimizaciones
- **Compresión**: Gzip/Brotli para assets
- **Cache Headers**: Headers apropiados para cache
- **CDN**: Distribución global de assets
- **Lazy Loading**: Carga diferida de componentes

## 📋 Checklist de PWA

### ✅ Implementado
- [x] Service Worker con cache offline
- [x] Web App Manifest
- [x] Instalación como app
- [x] Funcionalidad offline completa
- [x] Sincronización automática
- [x] Notificaciones push
- [x] Cache inteligente
- [x] Indicadores de estado offline

### 🔄 En Desarrollo
- [ ] Background sync avanzado
- [ ] Push notifications del servidor
- [ ] Métricas de PWA
- [ ] Testing automatizado

### 📋 Pendiente
- [ ] Workbox para cache avanzado
- [ ] Service Worker con TypeScript
- [ ] Métricas de rendimiento offline
- [ ] Testing de accesibilidad PWA

## 🐛 Troubleshooting

### Problemas Comunes

#### Service Worker no se registra
```bash
# Verificar en DevTools
Application > Service Workers
# Verificar errores en Console
```

#### Cache no funciona
```bash
# Limpiar cache
Application > Storage > Clear storage
# Verificar estrategias de cache
```

#### Instalación no aparece
```bash
# Verificar manifest
Application > Manifest
# Verificar criterios de instalación
```

#### Offline no funciona
```bash
# Verificar service worker
# Verificar cache storage
# Verificar localStorage
```

## 📚 Recursos Adicionales

### Documentación
- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev PWA](https://web.dev/progressive-web-apps/)
- [Workbox](https://developers.google.com/web/tools/workbox)

### Herramientas
- [Lighthouse PWA Audit](https://developers.google.com/web/tools/lighthouse)
- [PWA Builder](https://www.pwabuilder.com/)
- [Service Worker DevTools](https://github.com/GoogleChromeLabs/ndb)

### Comunidad
- [PWA Community](https://pwa-community.github.io/)
- [Stack Overflow PWA](https://stackoverflow.com/questions/tagged/progressive-web-apps)

---

**Desarrollado con ❤️ para Innexia Business Model Canvas**


