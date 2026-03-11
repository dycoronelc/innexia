#!/usr/bin/env python3
"""
Script para insertar datos maestros en las tablas de categorías, etiquetas, ubicaciones y estados
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models import Category, Tag, Location, Status

def insert_master_data():
    """Insertar datos maestros en las tablas"""
    print("🚀 Insertando datos maestros...")
    
    # Crear tablas si no existen
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Insertar Categorías
        print("📂 Insertando categorías...")
        categories = [
            Category(name="Tecnología", description="Proyectos relacionados con tecnología e innovación", color="#3B82F6", icon="computer"),
            Category(name="Negocios", description="Proyectos de emprendimiento y desarrollo empresarial", color="#10B981", icon="business"),
            Category(name="Educación", description="Proyectos educativos y de formación", color="#F59E0B", icon="school"),
            Category(name="Salud", description="Proyectos relacionados con salud y bienestar", color="#EF4444", icon="health"),
            Category(name="Medio Ambiente", description="Proyectos de sostenibilidad y conservación", color="#059669", icon="eco"),
            Category(name="Arte y Cultura", description="Proyectos culturales y artísticos", color="#8B5CF6", icon="palette"),
            Category(name="Investigación", description="Proyectos de investigación y desarrollo", color="#6366F1", icon="science"),
            Category(name="Otros", description="Otros tipos de proyectos", color="#6B7280", icon="more")
        ]
        
        for category in categories:
            existing = db.query(Category).filter(Category.name == category.name).first()
            if not existing:
                db.add(category)
                print(f"   ✅ Categoría: {category.name}")
        
        # Insertar Etiquetas
        print("🏷️ Insertando etiquetas...")
        tags = [
            Tag(name="Innovación", description="Proyectos innovadores", color="#8B5CF6"),
            Tag(name="Startup", description="Proyectos de startups", color="#F59E0B"),
            Tag(name="Sostenible", description="Proyectos sostenibles", color="#10B981"),
            Tag(name="Digital", description="Transformación digital", color="#3B82F6"),
            Tag(name="Social", description="Impacto social", color="#EF4444"),
            Tag(name="Global", description="Alcance global", color="#6366F1"),
            Tag(name="Local", description="Alcance local", color="#8B5CF6"),
            Tag(name="Urgente", description="Proyectos urgentes", color="#DC2626"),
            Tag(name="Prioritario", description="Proyectos prioritarios", color="#F59E0B"),
            Tag(name="Experimental", description="Proyectos experimentales", color="#8B5CF6")
        ]
        
        for tag in tags:
            existing = db.query(Tag).filter(Tag.name == tag.name).first()
            if not existing:
                db.add(tag)
                print(f"   ✅ Etiqueta: {tag.name}")
        
        # Insertar Ubicaciones
        print("📍 Insertando ubicaciones...")
        locations = [
            Location(name="Ciudad de México", country="México", state="CDMX", city="Ciudad de México", timezone="America/Mexico_City"),
            Location(name="Monterrey", country="México", state="Nuevo León", city="Monterrey", timezone="America/Mexico_City"),
            Location(name="Guadalajara", country="México", state="Jalisco", city="Guadalajara", timezone="America/Mexico_City"),
            Location(name="Barcelona", country="España", state="Cataluña", city="Barcelona", timezone="Europe/Madrid"),
            Location(name="Madrid", country="España", state="Madrid", city="Madrid", timezone="Europe/Madrid"),
            Location(name="Nueva York", country="Estados Unidos", state="Nueva York", city="Nueva York", timezone="America/New_York"),
            Location(name="San Francisco", country="Estados Unidos", state="California", city="San Francisco", timezone="America/Los_Angeles"),
            Location(name="Londres", country="Reino Unido", state="Inglaterra", city="Londres", timezone="Europe/London"),
            Location(name="Remoto", description="Trabajo remoto", timezone="UTC"),
            Location(name="Híbrido", description="Trabajo híbrido", timezone="UTC")
        ]
        
        for location in locations:
            existing = db.query(Location).filter(Location.name == location.name).first()
            if not existing:
                db.add(location)
                print(f"   ✅ Ubicación: {location.name}")
        
        # Insertar Estados
        print("🔄 Insertando estados...")
        statuses = [
            Status(name="Borrador", description="Proyecto en fase de planificación", color="#6B7280", icon="draft", order=1),
            Status(name="Activo", description="Proyecto en ejecución", color="#10B981", icon="play", order=2),
            Status(name="En Pausa", description="Proyecto temporalmente detenido", color="#F59E0B", icon="pause", order=3),
            Status(name="En Revisión", description="Proyecto en fase de revisión", color="#3B82F6", icon="review", order=4),
            Status(name="Completado", description="Proyecto finalizado exitosamente", color="#059669", icon="check", order=5, is_final=True),
            Status(name="Cancelado", description="Proyecto cancelado", color="#DC2626", icon="close", order=6, is_final=True),
            Status(name="Archivado", description="Proyecto archivado", color="#6B7280", icon="archive", order=7, is_final=True)
        ]
        
        for status in statuses:
            existing = db.query(Status).filter(Status.name == status.name).first()
            if not existing:
                db.add(status)
                print(f"   ✅ Estado: {status.name}")
        
        # Commit de todos los cambios
        db.commit()
        print("✅ Datos maestros insertados exitosamente")
        
        # Mostrar resumen
        print("\n📊 Resumen de datos insertados:")
        print(f"   📂 Categorías: {db.query(Category).count()}")
        print(f"   🏷️ Etiquetas: {db.query(Tag).count()}")
        print(f"   📍 Ubicaciones: {db.query(Location).count()}")
        print(f"   🔄 Estados: {db.query(Status).count()}")
        
    except Exception as e:
        print(f"❌ Error insertando datos maestros: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = insert_master_data()
    if success:
        print("\n🎉 ¡Datos maestros configurados exitosamente!")
        print("📝 Ahora puedes ejecutar: python init_db.py")
    else:
        print("\n💥 Error en la configuración de datos maestros")
        sys.exit(1)
