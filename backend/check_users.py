#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User
from app.core.auth import verify_password

def check_users():
    """Verificar usuarios en la base de datos"""
    db = next(get_db())
    
    try:
        # Obtener todos los usuarios
        users = db.query(User).all()
        
        print(f"Total de usuarios en la base de datos: {len(users)}")
        
        if users:
            print("\nUsuarios encontrados:")
            for user in users:
                print(f"- ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Company ID: {user.company_id}")
                print(f"  Active: {user.active}")
                print(f"  Role: {user.role}")
                print("---")
        else:
            print("No hay usuarios en la base de datos")
            
        # Verificar usuario admin específico
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print(f"\nUsuario 'admin' encontrado:")
            print(f"- ID: {admin_user.id}")
            print(f"- Email: {admin_user.email}")
            print(f"- Company ID: {admin_user.company_id}")
            print(f"- Active: {admin_user.active}")
            print(f"- Role: {admin_user.role}")
            
            # Verificar contraseña
            if verify_password("admin123", admin_user.hashed_password):
                print("✅ Contraseña 'admin123' es correcta")
            else:
                print("❌ Contraseña 'admin123' es incorrecta")
        else:
            print("❌ Usuario 'admin' no encontrado")
            
    except Exception as e:
        print(f"Error al verificar usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()

