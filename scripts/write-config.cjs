#!/usr/bin/env node
// Escribe public/config.js con VITE_API_BASE_URL para que la app use la URL correcta en producción (Railway).
const fs = require('fs');
const path = require('path');

const url = process.env.VITE_API_BASE_URL || 'http://localhost:8000';
const isRailway = process.env.RAILWAY_ENVIRONMENT != null || process.env.RAILWAY_PROJECT_ID != null;

if (isRailway && (!process.env.VITE_API_BASE_URL || url === 'http://localhost:8000')) {
  console.error('');
  console.error('ERROR: En Railway debes definir la variable VITE_API_BASE_URL en el servicio frontend.');
  console.error('Ejemplo: https://backend-production-xxxx.up.railway.app');
  console.error('Variables → Añadir → VITE_API_BASE_URL = URL de tu backend');
  console.error('');
  process.exit(1);
}

const content = `// Generado en build - no editar\nwindow.__INNEXIA_API_BASE_URL__ = ${JSON.stringify(url)};\n`;
const out = path.join(process.cwd(), 'public', 'config.js');
fs.writeFileSync(out, content);
console.log('config.js escrito con API URL:', url);
