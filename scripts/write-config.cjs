#!/usr/bin/env node
// Escribe public/config.js con VITE_API_BASE_URL para que la app use la URL correcta en producción (Railway).
const fs = require('fs');
const path = require('path');
const url = process.env.VITE_API_BASE_URL || 'http://localhost:8000';
const content = `// Generado en build - no editar\nwindow.__INNEXIA_API_BASE_URL__ = ${JSON.stringify(url)};\n`;
const out = path.join(process.cwd(), 'public', 'config.js');
fs.writeFileSync(out, content);
console.log('config.js escrito con API URL:', url);
