#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo
"""
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, create_tables
from app.models import User, Project, ProjectActivity, ProjectDocument, BusinessModelCanvas, ProjectTag, Category, Tag, Location, Status
from app.core.auth import get_password_hash

def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    print("🚀 Inicializando base de datos...")
    
    # Crear tablas
    try:
        create_tables()
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar si ya existen datos
        existing_user = db.query(User).first()
        if existing_user:
            print("⚠️ La base de datos ya contiene datos. Saltando inicialización.")
            return
        
        print("📝 Creando datos de ejemplo...")
        
        # Crear usuario administrador
        admin_user = User(
            username="admin",
            email="admin@innovai.com",
            full_name="Administrador del Sistema",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            active=True
        )
        db.add(admin_user)
        db.flush()  # Para obtener el ID
        
        # Crear usuario regular
        regular_user = User(
            username="usuario1",
            email="usuario1@innovai.com",
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
        
        if not technology_category or not remote_location or not active_status:
            print("❌ Error: No se encontraron los datos maestros necesarios")
            print("💡 Ejecuta primero: python insert_master_data.py")
            return
        
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
                **activity_data,
                assignee_id=regular_user.id,
                project_id=project.id
            )
            db.add(activity)
        
        # Crear Business Model Canvas
        bmc = BusinessModelCanvas(
            project_id=project.id,
            key_partners="Desarrolladores, Diseñadores UX/UI",
            key_activities="Desarrollo de software, Investigación de mercado",
            key_resources="Equipo de desarrollo, Infraestructura tecnológica",
            value_propositions="Plataforma intuitiva y eficiente para gestión de proyectos",
            customer_relationships="Soporte personalizado, Comunidad activa",
            channels="Plataforma web, Aplicación móvil, Redes sociales",
            customer_segments="Startups, Empresas medianas, Consultores",
            cost_structure="Desarrollo, Marketing, Operaciones",
            revenue_streams="Suscripciones, Licencias empresariales, Servicios de consultoría"
        )
        db.add(bmc)
        
        # Crear documento de ejemplo
        document = ProjectDocument(
            name="Documento de Requisitos",
            original_name="requisitos_proyecto.pdf",
            file_path="uploads/requisitos_proyecto.pdf",
            file_type=".pdf",
            file_size=1024000,  # 1MB
            description="Documento detallado de requisitos del proyecto",
            project_id=project.id,
            uploader_id=admin_user.id
        )
        db.add(document)
        
        # Confirmar cambios
        db.commit()
        print("✅ Base de datos inicializada exitosamente con datos de ejemplo")
        print(f"👤 Usuario admin creado: admin / admin123")
        print(f"👤 Usuario regular creado: usuario1 / usuario123")
        print(f"📁 Proyecto creado: {project.name}")
        print(f"📊 {len(activities)} actividades creadas")
        print(f"🏗️ Business Model Canvas creado")
        print(f"📄 Documento de ejemplo creado")
        
    except Exception as e:
        print(f"❌ Error al inicializar datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
