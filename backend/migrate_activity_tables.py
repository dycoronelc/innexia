#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar las nuevas tablas de actividades tipo Trello
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import *
from sqlalchemy import text

def create_new_tables():
    """Crear las nuevas tablas para las funcionalidades de actividades tipo Trello"""
    
    print("🔧 Creando nuevas tablas para actividades tipo Trello...")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Todas las tablas creadas exitosamente")
        
        # Verificar que las tablas se crearon
        new_tables = [
            "activity_assignees",
            "activity_tags", 
            "activity_labels",
            "activity_comments",
            "activity_checklists",
            "activity_checklist_items",
            "activity_attachments"
        ]
        
        with engine.connect() as conn:
            for table_name in new_tables:
                result = conn.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
                if result.fetchone():
                    print(f"✅ Tabla '{table_name}' creada correctamente")
                else:
                    print(f"❌ Error: Tabla '{table_name}' no se creó")
                    
    except Exception as e:
        print(f"❌ Error creando las tablas: {e}")
        return False
    
    return True

def add_sample_data():
    """Agregar algunos datos de ejemplo para probar las nuevas funcionalidades"""
    
    print("\n📝 Agregando datos de ejemplo...")
    
    try:
        db = SessionLocal()
        
        # Obtener algunos datos existentes
        users = db.query(User).limit(3).all()
        tags = db.query(Tag).limit(3).all()
        categories = db.query(Category).limit(3).all()
        activities = db.query(ProjectActivity).limit(2).all()
        
        if not activities:
            print("⚠️  No hay actividades para agregar datos de ejemplo")
            return True
        
        # Agregar algunos comentarios de ejemplo
        for activity in activities:
            for i, user in enumerate(users[:2]):
                comment = ActivityComment(
                    activity_id=activity.id,
                    author_id=user.id,
                    content=f"Comentario de ejemplo {i+1} para la actividad '{activity.title}'"
                )
                db.add(comment)
        
        # Agregar algunos checklists de ejemplo
        for activity in activities:
            checklist = ActivityChecklist(
                activity_id=activity.id,
                title="Tareas pendientes"
            )
            db.add(checklist)
            db.flush()  # Para obtener el ID del checklist
            
            # Agregar algunos items al checklist
            items = [
                "Revisar documentación",
                "Preparar presentación",
                "Coordinar con el equipo"
            ]
            
            for item_content in items:
                item = ActivityChecklistItem(
                    checklist_id=checklist.id,
                    content=item_content,
                    completed=False
                )
                db.add(item)
        
        # Agregar algunas etiquetas de ejemplo
        for activity in activities:
            for tag in tags[:2]:
                activity_tag = ActivityTag(
                    activity_id=activity.id,
                    tag_id=tag.id
                )
                db.add(activity_tag)
        
        # Agregar algunas etiquetas de color (labels) de ejemplo
        for activity in activities:
            for category in categories[:2]:
                label = ActivityLabel(
                    activity_id=activity.id,
                    category_id=category.id
                )
                db.add(label)
        
        db.commit()
        print("✅ Datos de ejemplo agregados correctamente")
        db.close()
        
    except Exception as e:
        print(f"❌ Error agregando datos de ejemplo: {e}")
        return False
    
    return True

def main():
    """Función principal de migración"""
    
    print("🚀 Iniciando migración de base de datos para actividades tipo Trello")
    print("=" * 60)
    
    # Paso 1: Crear nuevas tablas
    if not create_new_tables():
        print("❌ Falló la creación de tablas")
        return
    
    # Paso 2: Agregar datos de ejemplo
    if not add_sample_data():
        print("❌ Falló la adición de datos de ejemplo")
        return
    
    print("\n" + "=" * 60)
    print("🎉 ¡Migración completada exitosamente!")
    print("\n📋 Resumen de cambios:")
    print("✅ Nuevas tablas creadas:")
    print("   - activity_assignees (múltiples asignados)")
    print("   - activity_tags (etiquetas)")
    print("   - activity_labels (etiquetas de color)")
    print("   - activity_comments (comentarios)")
    print("   - activity_checklists (listas de tareas)")
    print("   - activity_checklist_items (tareas individuales)")
    print("   - activity_attachments (adjuntos)")
    print("\n✅ Datos de ejemplo agregados")
    print("\n🔧 La base de datos está lista para las nuevas funcionalidades de Trello!")

if __name__ == "__main__":
    main()
