#!/usr/bin/env python3
"""Verifica si un hash de la BD corresponde a la contraseña admin123."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.core.auth import verify_password

def main():
    if len(sys.argv) > 1:
        hash_bd = sys.argv[1].strip()
    else:
        print("Pega el hash de la BD (hashed_password) y pulsa Enter:")
        hash_bd = sys.stdin.read().strip().replace("\r", "").replace("\n", "")
    if not hash_bd:
        print("No se recibió ningún hash.")
        sys.exit(1)
    print("Longitud del hash:", len(hash_bd))
    print("Inicio del hash:", hash_bd[:14] if len(hash_bd) >= 14 else hash_bd)
    resultado = verify_password("admin123", hash_bd)
    print("Verificación admin123:", resultado)
    sys.exit(0 if resultado else 1)

if __name__ == "__main__":
    main()
