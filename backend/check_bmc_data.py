#!/usr/bin/env python3

from app.database import get_db
from app.models.business_model_canvas import BusinessModelCanvas
from app.models.project import Project

def check_bmc_data():
    db = next(get_db())
    
    # Verificar proyecto
    project = db.query(Project).filter(Project.id == 1).first()
    print(f"Proyecto ID 1: {project.name if project else 'No encontrado'}")
    
    # Verificar BMC
    bmc = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == 1).first()
    print(f"BMC para proyecto 1: {'Encontrado' if bmc else 'No encontrado'}")
    
    if bmc:
        print(f"BMC ID: {bmc.id}")
        print(f"Key Partners: {bmc.key_partners}")
        print(f"Value Propositions: {bmc.value_propositions}")
    
    # Listar todos los proyectos
    projects = db.query(Project).all()
    print(f"\nTotal de proyectos: {len(projects)}")
    for p in projects:
        print(f"- Proyecto {p.id}: {p.name}")
    
    # Listar todos los BMC
    bmcs = db.query(BusinessModelCanvas).all()
    print(f"\nTotal de BMC: {len(bmcs)}")
    for b in bmcs:
        print(f"- BMC {b.id}: Proyecto {b.project_id}")

if __name__ == "__main__":
    check_bmc_data()

