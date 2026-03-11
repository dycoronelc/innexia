#!/usr/bin/env python3
"""
Script para crear usuario admin de prueba
"""
import sys
import os
import warnings

# Suprimir warnings
warnings.filterwarnings("ignore")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.core.auth import get_password_hash
from sqlalchemy import text

def create_admin_user():
    """Crear usuario admin directamente con SQL"""
    
    try:
        # Hash de la contraseña admin123
        password_hash = get_password_hash("admin123")
        
        # SQL para insertar usuario admin
        sql = text("""
            INSERT IGNORE INTO users (
                username, 
                email, 
                full_name, 
                hashed_password, 
                role, 
                company_id, 
                active, 
                created_at
            ) VALUES (
                'admin',
                'admin@innovai.com',
                'Administrador',
                :password_hash,
                'admin',
                1,
                1,
                NOW()
            )
        """)
        
        with engine.connect() as conn:
            result = conn.execute(sql, {"password_hash": password_hash})
            conn.commit()
            
        print("✅ Usuario admin creado exitosamente")
        
        # Verificar que se creó
        check_sql = text("SELECT id, username, email, company_id, active FROM users WHERE username = 'admin'")
        with engine.connect() as conn:
            result = conn.execute(check_sql)
            user = result.fetchone()
            
        if user:
            print(f"✅ Usuario verificado: {user.username} (ID: {user.id}, Company: {user.company_id})")
        else:
            print("❌ Error: Usuario no encontrado después de crearlo")
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        import traceback
        traceback.print_exc()

def create_company():
    """Crear empresa de prueba"""
    
    try:
        sql = text("""
            INSERT IGNORE INTO companies (
                name,
                description,
                created_at
            ) VALUES (
                'InnovAI Demo',
                'Empresa de demostración',
                NOW()
            )
        """)
        
        with engine.connect() as conn:
            conn.execute(sql)
            conn.commit()
            
        print("✅ Empresa creada exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando empresa: {e}")

if __name__ == "__main__":
    print("Creando datos de prueba...")
    create_company()
    create_admin_user()
    print("¡Listo!")

