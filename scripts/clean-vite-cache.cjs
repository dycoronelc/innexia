#!/usr/bin/env node
// Elimina cachés dentro de node_modules para evitar EBUSY en Railway/Docker (npm ci intenta borrarlos)
const fs = require('fs');
const path = require('path');
const dirs = ['.vite', '.cache'];
const base = path.join(process.cwd(), 'node_modules');
dirs.forEach((name) => {
  const dir = path.join(base, name);
  try {
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true, force: true });
      console.log('Eliminado node_modules/' + name);
    }
  } catch (e) {
    // Ignorar si está bloqueado
  }
});
