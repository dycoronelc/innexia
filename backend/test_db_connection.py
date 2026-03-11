import pymysql

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def test_database_connection():
    """Probar la conexión a la base de datos"""
    try:
        # Conectar a la base de datos bmc
        connection = pymysql.connect(**DB_CONFIG, database='bmc')
        cursor = connection.cursor()
        
        print("✅ Conexión a la base de datos 'bmc' exitosa")
        
        # Verificar que las tablas existen
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"📊 Tablas encontradas en la base de datos 'bmc': {len(tables)}")
        for table in tables:
            table_name = list(table.values())[0]
            print(f"  - {table_name}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()

