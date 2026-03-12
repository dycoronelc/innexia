#!/usr/bin/env python3
"""Genera un hash bcrypt para guardar en la BD (tabla users, columna hashed_password)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.core.auth import get_password_hash

def main():
    password = sys.argv[1] if len(sys.argv) > 1 else "admin123"
    h = get_password_hash(password)
    print(h)

if __name__ == "__main__":
    main()
