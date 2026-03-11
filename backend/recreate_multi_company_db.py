#!/usr/bin/env python3
"""
Script para recrear la base de datos con el sistema multiempresas
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, drop_tables, create_tables
from app.models import Company, User, Project, ProjectActivity, ProjectDocument, BusinessModelCanvas, ProjectTag, Category, Tag, Location, Status
from app.core.auth import get_password_hash
from datetime import datetime, timedelta

def recreate_multi_company_database():
    """Recrear la base de datos con el sistema multiempresas"""
    print("🚀 Recreando base de datos con sistema multiempresas...")
    
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
        
        print("🎉 ¡Base de datos multiempresas recreada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error recreando base de datos: {e}")
        return False
    
    return True

def insert_master_data():
    """Insertar datos maestros"""
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Crear empresa principal (Innexia)
        print("🏢 Creando empresa principal...")
        innexia_company = Company(
            name="Innexia",
            slug="innexia",
            description="Empresa líder en gestión de proyectos innovadores",
            primary_color="#4D2581",
            secondary_color="#ED682B",
            industry="Tecnología",
            website="https://innexia.com",
            email="info@innexia.com",
            country="México",
            state="CDMX",
            city="Ciudad de México",
            timezone="America/Mexico_City",
            subscription_plan="enterprise",
            max_users=1000,
            max_projects=10000,
            max_storage_gb=100
        )
        db.add(innexia_company)
        db.flush()
        print(f"   ✅ Empresa creada: {innexia_company.name}")
        
        # Crear empresa de ejemplo (TechCorp)
        print("🏢 Creando empresa de ejemplo...")
        techcorp_company = Company(
            name="TechCorp",
            slug="techcorp",
            description="Empresa de tecnología innovadora",
            primary_color="#3B82F6",
            secondary_color="#10B981",
            industry="Tecnología",
            website="https://techcorp.com",
            email="info@techcorp.com",
            country="Estados Unidos",
            state="California",
            city="San Francisco",
            timezone="America/Los_Angeles",
            subscription_plan="pro",
            max_users=100,
            max_projects=500,
            max_storage_gb=20
        )
        db.add(techcorp_company)
        db.flush()
        print(f"   ✅ Empresa creada: {techcorp_company.name}")
        
        # Insertar Categorías para Innexia
        print("📂 Insertando categorías para Innexia...")
        innexia_categories = [
            Category(name="Tecnología", company_id=innexia_company.id, description="Proyectos relacionados con tecnología e innovación", color="#3B82F6", icon="computer"),
            Category(name="Negocios", company_id=innexia_company.id, description="Proyectos de emprendimiento y desarrollo empresarial", color="#10B981", icon="business"),
            Category(name="Educación", company_id=innexia_company.id, description="Proyectos educativos y de formación", color="#F59E0B", icon="school"),
            Category(name="Salud", company_id=innexia_company.id, description="Proyectos relacionados con salud y bienestar", color="#EF4444", icon="health"),
            Category(name="Medio Ambiente", company_id=innexia_company.id, description="Proyectos de sostenibilidad y conservación", color="#059669", icon="eco"),
            Category(name="Arte y Cultura", company_id=innexia_company.id, description="Proyectos culturales y artísticos", color="#8B5CF6", icon="palette"),
            Category(name="Investigación", company_id=innexia_company.id, description="Proyectos de investigación y desarrollo", color="#6366F1", icon="science"),
            Category(name="Otros", company_id=innexia_company.id, description="Otros tipos de proyectos", color="#6B7280", icon="more")
        ]
        
        for category in innexia_categories:
            db.add(category)
        
        # Insertar Categorías para TechCorp
        print("📂 Insertando categorías para TechCorp...")
        techcorp_categories = [
            Category(name="Desarrollo Web", company_id=techcorp_company.id, description="Proyectos de desarrollo web", color="#3B82F6", icon="web"),
            Category(name="Aplicaciones Móviles", company_id=techcorp_company.id, description="Proyectos de apps móviles", color="#10B981", icon="mobile"),
            Category(name="Inteligencia Artificial", company_id=techcorp_company.id, description="Proyectos de IA y ML", color="#8B5CF6", icon="ai"),
            Category(name="Cloud Computing", company_id=techcorp_company.id, description="Proyectos de infraestructura cloud", color="#F59E0B", icon="cloud")
        ]
        
        for category in techcorp_categories:
            db.add(category)
        
        # Insertar Etiquetas para Innexia
        print("🏷️ Insertando etiquetas para Innexia...")
        innexia_tags = [
            Tag(name="Innovación", company_id=innexia_company.id, description="Proyectos innovadores", color="#8B5CF6"),
            Tag(name="Startup", company_id=innexia_company.id, description="Proyectos de startups", color="#F59E0B"),
            Tag(name="Sostenible", company_id=innexia_company.id, description="Proyectos sostenibles", color="#10B981"),
            Tag(name="Digital", company_id=innexia_company.id, description="Transformación digital", color="#3B82F6"),
            Tag(name="Social", company_id=innexia_company.id, description="Impacto social", color="#EF4444"),
            Tag(name="Global", company_id=innexia_company.id, description="Alcance global", color="#6366F1"),
            Tag(name="Local", company_id=innexia_company.id, description="Alcance local", color="#8B5CF6"),
            Tag(name="Urgente", company_id=innexia_company.id, description="Proyectos urgentes", color="#DC2626"),
            Tag(name="Prioritario", company_id=innexia_company.id, description="Proyectos prioritarios", color="#F59E0B"),
            Tag(name="Experimental", company_id=innexia_company.id, description="Proyectos experimentales", color="#8B5CF6")
        ]
        
        for tag in innexia_tags:
            db.add(tag)
        
        # Insertar Etiquetas para TechCorp
        print("🏷️ Insertando etiquetas para TechCorp...")
        techcorp_tags = [
            Tag(name="React", company_id=techcorp_company.id, description="Proyectos con React", color="#61DAFB"),
            Tag(name="Python", company_id=techcorp_company.id, description="Proyectos con Python", color="#3776AB"),
            Tag(name="Machine Learning", company_id=techcorp_company.id, description="Proyectos de ML", color="#FF6B6B"),
            Tag(name="DevOps", company_id=techcorp_company.id, description="Proyectos de DevOps", color="#00D4AA")
        ]
        
        for tag in techcorp_tags:
            db.add(tag)
        
        # Insertar Ubicaciones para Innexia
        print("📍 Insertando ubicaciones para Innexia...")
        innexia_locations = [
            Location(name="Ciudad de México", company_id=innexia_company.id, country="México", state="CDMX", city="Ciudad de México", timezone="America/Mexico_City"),
            Location(name="Monterrey", company_id=innexia_company.id, country="México", state="Nuevo León", city="Monterrey", timezone="America/Mexico_City"),
            Location(name="Guadalajara", company_id=innexia_company.id, country="México", state="Jalisco", city="Guadalajara", timezone="America/Mexico_City"),
            Location(name="Remoto", company_id=innexia_company.id, description="Trabajo remoto", timezone="UTC"),
            Location(name="Híbrido", company_id=innexia_company.id, description="Trabajo híbrido", timezone="UTC")
        ]
        
        for location in innexia_locations:
            db.add(location)
        
        # Insertar Ubicaciones para TechCorp
        print("📍 Insertando ubicaciones para TechCorp...")
        techcorp_locations = [
            Location(name="San Francisco", company_id=techcorp_company.id, country="Estados Unidos", state="California", city="San Francisco", timezone="America/Los_Angeles"),
            Location(name="Nueva York", company_id=techcorp_company.id, country="Estados Unidos", state="Nueva York", city="Nueva York", timezone="America/New_York"),
            Location(name="Remoto", company_id=techcorp_company.id, description="Trabajo remoto", timezone="UTC")
        ]
        
        for location in techcorp_locations:
            db.add(location)
        
        # Insertar Estados para Innexia
        print("🔄 Insertando estados para Innexia...")
        innexia_statuses = [
            Status(name="Borrador", company_id=innexia_company.id, description="Proyecto en fase de planificación", color="#6B7280", icon="draft", order=1),
            Status(name="Activo", company_id=innexia_company.id, description="Proyecto en ejecución", color="#10B981", icon="play", order=2),
            Status(name="En Pausa", company_id=innexia_company.id, description="Proyecto temporalmente detenido", color="#F59E0B", icon="pause", order=3),
            Status(name="En Revisión", company_id=innexia_company.id, description="Proyecto en fase de revisión", color="#3B82F6", icon="review", order=4),
            Status(name="Completado", company_id=innexia_company.id, description="Proyecto finalizado exitosamente", color="#059669", icon="check", order=5, is_final=True),
            Status(name="Cancelado", company_id=innexia_company.id, description="Proyecto cancelado", color="#DC2626", icon="close", order=6, is_final=True),
            Status(name="Archivado", company_id=innexia_company.id, description="Proyecto archivado", color="#6B7280", icon="archive", order=7, is_final=True)
        ]
        
        for status in innexia_statuses:
            db.add(status)
        
        # Insertar Estados para TechCorp
        print("🔄 Insertando estados para TechCorp...")
        techcorp_statuses = [
            Status(name="Planning", company_id=techcorp_company.id, description="Project in planning phase", color="#6B7280", icon="planning", order=1),
            Status(name="In Progress", company_id=techcorp_company.id, description="Project in development", color="#3B82F6", icon="development", order=2),
            Status(name="Testing", company_id=techcorp_company.id, description="Project in testing phase", color="#F59E0B", icon="testing", order=3),
            Status(name="Deployed", company_id=techcorp_company.id, description="Project deployed to production", color="#10B981", icon="deployed", order=4, is_final=True),
            Status(name="On Hold", company_id=techcorp_company.id, description="Project temporarily suspended", color="#EF4444", icon="hold", order=5)
        ]
        
        for status in techcorp_statuses:
            db.add(status)
        
        db.commit()
        print("✅ Datos maestros insertados")
        
        return innexia_company, techcorp_company
        
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
        # Obtener empresas
        innexia_company = db.query(Company).filter(Company.slug == "innexia").first()
        techcorp_company = db.query(Company).filter(Company.slug == "techcorp").first()
        
        # Crear super admin (puede acceder a todas las empresas)
        print("👑 Creando super administrador...")
        super_admin = User(
            username="superadmin",
            email="superadmin@innexia.com",
            full_name="Super Administrador",
            hashed_password=get_password_hash("superadmin123"),
            role="super_admin",
            company_id=innexia_company.id,
            active=True
        )
        db.add(super_admin)
        db.flush()
        
        # Crear usuario admin para Innexia
        print("👤 Creando admin para Innexia...")
        innexia_admin = User(
            username="admin",
            email="admin@innexia.com",
            full_name="Administrador Innexia",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            company_id=innexia_company.id,
            active=True
        )
        db.add(innexia_admin)
        db.flush()
        
        # Crear usuario regular para Innexia
        print("👤 Creando usuario para Innexia...")
        innexia_user = User(
            username="usuario1",
            email="usuario1@innexia.com",
            full_name="Usuario Innexia",
            hashed_password=get_password_hash("usuario123"),
            role="user",
            company_id=innexia_company.id,
            active=True
        )
        db.add(innexia_user)
        db.flush()
        
        # Crear usuario admin para TechCorp
        print("👤 Creando admin para TechCorp...")
        techcorp_admin = User(
            username="techcorp_admin",
            email="admin@techcorp.com",
            full_name="Administrador TechCorp",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            company_id=techcorp_company.id,
            active=True
        )
        db.add(techcorp_admin)
        db.flush()
        
        # Obtener datos maestros necesarios para Innexia
        technology_category = db.query(Category).filter(Category.name == "Tecnología", Category.company_id == innexia_company.id).first()
        remote_location = db.query(Location).filter(Location.name == "Remoto", Location.company_id == innexia_company.id).first()
        active_status = db.query(Status).filter(Status.name == "Activo", Status.company_id == innexia_company.id).first()
        
        # Crear proyecto de ejemplo para Innexia
        print("📁 Creando proyecto para Innexia...")
        innexia_project = Project(
            name="Proyecto Innexia",
            description="Desarrollo de una plataforma de gestión de proyectos innovadora",
            company_id=innexia_company.id,
            category_id=technology_category.id,
            location_id=remote_location.id,
            status_id=active_status.id,
            owner_id=innexia_admin.id
        )
        db.add(innexia_project)
        db.flush()
        
        # Crear etiquetas para el proyecto de Innexia
        tag_names = ["Innovación", "Tecnología", "Gestión", "Startup"]
        for tag_name in tag_names:
            tag_master = db.query(Tag).filter(Tag.name == tag_name, Tag.company_id == innexia_company.id).first()
            if tag_master:
                project_tag = ProjectTag(project_id=innexia_project.id, tag_id=tag_master.id)
                db.add(project_tag)
        
        # Obtener datos maestros necesarios para TechCorp
        web_category = db.query(Category).filter(Category.name == "Desarrollo Web", Category.company_id == techcorp_company.id).first()
        sf_location = db.query(Location).filter(Location.name == "San Francisco", Location.company_id == techcorp_company.id).first()
        in_progress_status = db.query(Status).filter(Status.name == "In Progress", Status.company_id == techcorp_company.id).first()
        
        # Crear proyecto de ejemplo para TechCorp
        print("📁 Creando proyecto para TechCorp...")
        techcorp_project = Project(
            name="E-commerce Platform",
            description="Modern e-commerce platform built with React and Node.js",
            company_id=techcorp_company.id,
            category_id=web_category.id,
            location_id=sf_location.id,
            status_id=in_progress_status.id,
            owner_id=techcorp_admin.id
        )
        db.add(techcorp_project)
        db.flush()
        
        # Crear etiquetas para el proyecto de TechCorp
        techcorp_tag_names = ["React", "Python", "Machine Learning"]
        for tag_name in techcorp_tag_names:
            tag_master = db.query(Tag).filter(Tag.name == tag_name, Tag.company_id == techcorp_company.id).first()
            if tag_master:
                project_tag = ProjectTag(project_id=techcorp_project.id, tag_id=tag_master.id)
                db.add(project_tag)
        
        # Crear Business Model Canvas para Innexia
        print("🏗️ Creando BMC para Innexia...")
        innexia_bmc = BusinessModelCanvas(
            project_id=innexia_project.id,
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
        db.add(innexia_bmc)
        
        # Crear Business Model Canvas para TechCorp
        print("🏗️ Creando BMC para TechCorp...")
        techcorp_bmc = BusinessModelCanvas(
            project_id=techcorp_project.id,
            key_partners="Payment processors, Shipping companies",
            key_activities="Platform development, Customer support",
            key_resources="Development team, Cloud infrastructure",
            value_propositions="Modern, scalable e-commerce solution",
            customer_relationships="24/7 support, Community forums",
            channels="Direct sales, Partner network",
            customer_segments="Small businesses, Mid-market companies",
            cost_structure="Development, Infrastructure, Marketing",
            revenue_streams="Monthly subscriptions, Transaction fees"
        )
        db.add(techcorp_bmc)
        
        db.commit()
        print("✅ Datos de ejemplo insertados")
        
        # Mostrar resumen
        print(f"\n👑 Super Admin creado: superadmin / superadmin123")
        print(f"👤 Admin Innexia: admin / admin123")
        print(f"👤 Usuario Innexia: usuario1 / usuario123")
        print(f"👤 Admin TechCorp: techcorp_admin / admin123")
        print(f"📁 Proyecto Innexia: {innexia_project.name}")
        print(f"📁 Proyecto TechCorp: {techcorp_project.name}")
        print(f"🏗️ Business Model Canvas creados para ambas empresas")
        
    except Exception as e:
        print(f"❌ Error insertando datos de ejemplo: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    success = recreate_multi_company_database()
    if success:
        print("\n🎉 ¡Base de datos multiempresas recreada exitosamente!")
        print("\n📊 Resumen del sistema multiempresas:")
        print("   🏢 2 empresas creadas (Innexia y TechCorp)")
        print("   👥 4 usuarios creados con diferentes roles")
        print("   📁 2 proyectos de ejemplo")
        print("   🏗️ 2 Business Model Canvas")
        print("   📂 Categorías, etiquetas, ubicaciones y estados personalizados por empresa")
    else:
        print("\n💥 Error recreando la base de datos")
        sys.exit(1)
