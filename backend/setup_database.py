#!/usr/bin/env python3
"""
Script para configurar la base de datos MySQL
"""
import pymysql
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def setup_database():
    """Configurar la base de datos MySQL"""
    print("🚀 Configurando base de datos MySQL...")
    
    # Conectar a MySQL sin especificar base de datos
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        print("✅ Conexión a MySQL exitosa")
        
        with connection.cursor() as cursor:
            # Crear base de datos si no existe
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Base de datos '{DB_NAME}' creada/verificada")
            
            # Mostrar información de la base de datos
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            print(f"📊 Bases de datos disponibles: {', '.join(databases)}")
            
            # Seleccionar la base de datos
            cursor.execute(f"USE {DB_NAME}")
            print(f"🎯 Base de datos '{DB_NAME}' seleccionada")
            
            # Verificar permisos del usuario
            cursor.execute("SHOW GRANTS")
            grants = cursor.fetchall()
            print("🔐 Permisos del usuario:")
            for grant in grants:
                print(f"   {grant[0]}")
        
        connection.close()
        print("✅ Configuración de base de datos completada")
        
    except pymysql.Error as e:
        print(f"❌ Error de MySQL: {e}")
        print("\n🔧 Soluciones posibles:")
        print("   1. Verificar que MySQL esté ejecutándose")
        print("   2. Verificar las credenciales en el archivo .env")
        print("   3. Verificar que el usuario 'bmc' tenga permisos suficientes")
        print("   4. Crear el usuario manualmente:")
        print("      CREATE USER 'bmc'@'localhost' IDENTIFIED BY 'Innexia';")
        print("      GRANT ALL PRIVILEGES ON *.* TO 'bmc'@'localhost';")
        print("      FLUSH PRIVILEGES;")
        return False
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n🎉 ¡Base de datos configurada exitosamente!")
        print("📝 Ahora puedes ejecutar: python init_db.py")
    else:
        print("\n💥 Error en la configuración de la base de datos")
        sys.exit(1)

