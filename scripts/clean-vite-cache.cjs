#!/usr/bin/env node
// Elimina node_modules/.vite para evitar EBUSY cuando npm ci borra node_modules (Railway, Docker, etc.)
const fs = require('fs');
const path = require('path');
const dir = path.join(process.cwd(), 'node_modules', '.vite');
try {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
    console.log('Eliminado node_modules/.vite');
  }
} catch (e) {
  // Ignorar si está bloqueado; npm ci puede seguir
}
