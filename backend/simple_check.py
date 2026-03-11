#!/usr/bin/env python3
"""
Script simple para verificar usuarios
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User

def main():
    db = next(get_db())
    
    try:
        # Contar usuarios
        user_count = db.query(User).count()
        print(f"Total usuarios: {user_count}")
        
        # Buscar usuario admin
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print(f"Usuario admin encontrado: {admin.username}")
            print(f"Company ID: {admin.company_id}")
            print(f"Active: {admin.active}")
        else:
            print("Usuario admin NO encontrado")
            
        # Listar todos los usuarios
        users = db.query(User).all()
        for user in users:
            print(f"- {user.username} (ID: {user.id}, Company: {user.company_id})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

