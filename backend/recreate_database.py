#!/usr/bin/env python3
"""
Script para recrear la base de datos con la nueva estructura de tablas maestras
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, drop_tables, create_tables
from app.models import User, Project, ProjectActivity, ProjectDocument, BusinessModelCanvas, ProjectTag, Category, Tag, Location, Status
from app.core.auth import get_password_hash
from datetime import datetime, timedelta

def recreate_database():
    """Recrear la base de datos con la nueva estructura"""
    print("🚀 Recreando base de datos...")
    
    try:
        # Eliminar todas las tablas existentes
        print("🗑️ Eliminando tablas existentes...")
        drop_tables()
        print("✅ Tablas eliminadas")
        
        # Crear nuevas tablas
        print("🏗️ Creando nuevas tablas...")
        create_tables()
        print("✅ Nuevas tablas creadas")
        
        # Insertar datos maestros
        print("📝 Insertando datos maestros...")
        insert_master_data()
        
        # Insertar datos de ejemplo
        print("📝 Insertando datos de ejemplo...")
        insert_sample_data()
        
        print("🎉 ¡Base de datos recreada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error recreando base de datos: {e}")
        return False
    
    return True

def insert_master_data():
    """Insertar datos maestros"""
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Insertar Categorías
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
            db.add(category)
        
        # Insertar Etiquetas
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
            db.add(tag)
        
        # Insertar Ubicaciones
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
            db.add(location)
        
        # Insertar Estados
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
            db.add(status)
        
        db.commit()
        print("✅ Datos maestros insertados")
        
    except Exception as e:
        print(f"❌ Error insertando datos maestros: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def insert_sample_data():
    """Insertar datos de ejemplo"""
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Crear usuario administrador
        admin_user = User(
            username="admin",
            email="admin@innexia.com",
            full_name="Administrador del Sistema",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            active=True
        )
        db.add(admin_user)
        db.flush()
        
        # Crear usuario regular
        regular_user = User(
            username="usuario1",
            email="usuario1@innexia.com",
            full_name="Usuario Ejemplo",
            hashed_password=get_password_hash("usuario123"),
            role="user",
            active=True
        )
        db.add(regular_user)
        db.flush()
        
        # Obtener datos maestros necesarios
        technology_category = db.query(Category).filter(Category.name == "Tecnología").first()
        remote_location = db.query(Location).filter(Location.name == "Remoto").first()
        active_status = db.query(Status).filter(Status.name == "Activo").first()
        
        # Crear proyecto de ejemplo
        project = Project(
            name="Proyecto Innexia",
            description="Desarrollo de una plataforma de gestión de proyectos innovadora",
            category_id=technology_category.id,
            location_id=remote_location.id,
            status_id=active_status.id,
            owner_id=admin_user.id
        )
        db.add(project)
        db.flush()
        
        # Crear etiquetas para el proyecto
        tag_names = ["Innovación", "Tecnología", "Gestión", "Startup"]
        for tag_name in tag_names:
            tag_master = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag_master:
                project_tag = ProjectTag(project_id=project.id, tag_id=tag_master.id)
                db.add(project_tag)
        
        # Crear actividades del proyecto
        activities = [
            {
                "title": "Análisis de Requisitos",
                "description": "Recopilar y analizar los requisitos del proyecto",
                "status": "Completado",
                "priority": "Alta",
                "start_date": datetime.now() - timedelta(days=30),
                "due_date": datetime.now() - timedelta(days=20)
            },
            {
                "title": "Diseño de Arquitectura",
                "description": "Diseñar la arquitectura del sistema",
                "status": "En Progreso",
                "priority": "Alta",
                "start_date": datetime.now() - timedelta(days=15),
                "due_date": datetime.now() + timedelta(days=10)
            },
            {
                "title": "Desarrollo Frontend",
                "description": "Implementar la interfaz de usuario",
                "status": "Pendiente",
                "priority": "Media",
                "start_date": datetime.now() + timedelta(days=5),
                "due_date": datetime.now() + timedelta(days=25)
            }
        ]
        
        for activity_data in activities:
            activity = ProjectActivity(
                title=activity_data["title"],
                description=activity_data["description"],
                status=activity_data["status"],
                priority=activity_data["priority"],
                start_date=activity_data["start_date"],
                due_date=activity_data["due_date"],
                project_id=project.id,
                assignee_id=admin_user.id
            )
            db.add(activity)
        
        # Crear Business Model Canvas
        bmc = BusinessModelCanvas(
            project_id=project.id,
            key_partners="Desarrolladores, Diseñadores UX/UI",
            key_activities="Desarrollo de software, Testing, Documentación",
            key_resources="Equipo de desarrollo, Herramientas de desarrollo",
            value_propositions="Plataforma intuitiva y eficiente para gestión de proyectos",
            customer_relationships="Soporte técnico, Comunidad de usuarios",
            channels="Plataforma web, Aplicación móvil",
            customer_segments="Startups, Empresas medianas, Freelancers",
            cost_structure="Desarrollo, Infraestructura, Marketing",
            revenue_streams="Suscripciones premium, Servicios de consultoría"
        )
        db.add(bmc)
        
        # Crear documento de ejemplo
        document = ProjectDocument(
            name="Documento de Requisitos",
            original_name="requisitos.pdf",
            file_path="uploads/1/requisitos.pdf",
            file_type=".pdf",
            file_size=1024000,  # 1MB
            description="Documento detallado de requisitos del proyecto",
            project_id=project.id,
            uploader_id=admin_user.id
        )
        db.add(document)
        
        db.commit()
        print("✅ Datos de ejemplo insertados")
        
        # Mostrar resumen
        print(f"\n👤 Usuario admin creado: admin / admin123")
        print(f"👤 Usuario regular creado: usuario1 / usuario123")
        print(f"📁 Proyecto creado: {project.name}")
        print(f"📊 {len(activities)} actividades creadas")
        print(f"🏗️ Business Model Canvas creado")
        print(f"📄 Documento de ejemplo creado")
        
    except Exception as e:
        print(f"❌ Error insertando datos de ejemplo: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    success = recreate_database()
    if success:
        print("\n🎉 ¡Base de datos recreada exitosamente!")
    else:
        print("\n💥 Error recreando la base de datos")
        sys.exit(1)
