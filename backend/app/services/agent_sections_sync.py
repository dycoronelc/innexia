"""
Sincroniza las secciones del agente (estrategia comercial, roadmap, análisis financiero,
riesgos, veredicto) desde el JSON de project_agent_output a sus tablas canónicas.
Cada tabla es la fuente única para visualización y edición; el JSON en project_agent_output
queda como auditoría. Un futuro agente puede re-analizar y actualizar estas tablas.
"""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.project_estrategia_comercial import ProjectEstrategiaComercial
from ..models.project_roadmap import ProjectRoadmap
from ..models.project_analisis_financiero import ProjectAnalisisFinanciero
from ..models.project_analisis_riesgos import ProjectAnalisisRiesgos, ProjectRiesgo
from ..models.project_veredicto import ProjectVeredicto


def sync_agent_estrategia_comercial(project_id: int, data: Optional[Dict[str, Any]], db: Session) -> bool:
    if not data:
        return False
    existing = db.query(ProjectEstrategiaComercial).filter(ProjectEstrategiaComercial.project_id == project_id).first()
    if existing:
        existing.analisis_mercado = data.get("analisis_mercado")
        existing.estrategia_precios = data.get("estrategia_precios")
        existing.estrategia_marketing = data.get("estrategia_marketing")
        existing.estrategia_ventas = data.get("estrategia_ventas")
        db.commit()
        db.refresh(existing)
        return True
    row = ProjectEstrategiaComercial(
        project_id=project_id,
        analisis_mercado=data.get("analisis_mercado"),
        estrategia_precios=data.get("estrategia_precios"),
        estrategia_marketing=data.get("estrategia_marketing"),
        estrategia_ventas=data.get("estrategia_ventas"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return True


def sync_agent_roadmap(project_id: int, data: Optional[Dict[str, Any]], db: Session) -> bool:
    if not data:
        return False
    existing = db.query(ProjectRoadmap).filter(ProjectRoadmap.project_id == project_id).first()
    fases = data.get("fases")
    cronograma = data.get("cronograma_total_meses")
    if existing:
        existing.fases = fases
        existing.cronograma_total_meses = cronograma
        db.commit()
        db.refresh(existing)
        return True
    row = ProjectRoadmap(
        project_id=project_id,
        cronograma_total_meses=cronograma,
        fases=fases,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return True


def sync_agent_analisis_financiero(project_id: int, data: Optional[Dict[str, Any]], db: Session) -> bool:
    if not data:
        return False
    existing = db.query(ProjectAnalisisFinanciero).filter(ProjectAnalisisFinanciero.project_id == project_id).first()
    if existing:
        existing.inversion_inicial = data.get("inversion_inicial")
        existing.proyecciones_3_anos = data.get("proyecciones_3_anos")
        existing.metricas_clave = data.get("metricas_clave")
        existing.viabilidad_financiera = data.get("viabilidad_financiera")
        db.commit()
        db.refresh(existing)
        return True
    row = ProjectAnalisisFinanciero(
        project_id=project_id,
        inversion_inicial=data.get("inversion_inicial"),
        proyecciones_3_anos=data.get("proyecciones_3_anos"),
        metricas_clave=data.get("metricas_clave"),
        viabilidad_financiera=data.get("viabilidad_financiera"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return True


def sync_agent_analisis_riesgos(project_id: int, data: Optional[Dict[str, Any]], db: Session) -> bool:
    if not data:
        return False
    # Cabecera
    existing = db.query(ProjectAnalisisRiesgos).filter(ProjectAnalisisRiesgos.project_id == project_id).first()
    if existing:
        existing.nivel_riesgo_general = data.get("nivel_riesgo_general")
        existing.recomendaciones = data.get("recomendaciones")
        db.commit()
        db.refresh(existing)
    else:
        row = ProjectAnalisisRiesgos(
            project_id=project_id,
            nivel_riesgo_general=data.get("nivel_riesgo_general"),
            recomendaciones=data.get("recomendaciones"),
        )
        db.add(row)
        db.commit()

    # Riesgos: borrar existentes e insertar los del agente
    db.query(ProjectRiesgo).filter(ProjectRiesgo.project_id == project_id).delete()
    riesgos: List[Dict[str, Any]] = data.get("riesgos_identificados") or []
    for i, r in enumerate(riesgos):
        pr = ProjectRiesgo(
            project_id=project_id,
            categoria=r.get("categoria"),
            riesgo=r.get("riesgo"),
            probabilidad=r.get("probabilidad"),
            impacto=r.get("impacto"),
            mitigacion=r.get("mitigacion"),
            orden=i,
        )
        db.add(pr)
    db.commit()
    return True


def sync_agent_veredicto(project_id: int, data: Optional[Dict[str, Any]], db: Session) -> bool:
    if not data:
        return False
    existing = db.query(ProjectVeredicto).filter(ProjectVeredicto.project_id == project_id).first()
    if existing:
        existing.decision = data.get("decision")
        existing.puntuacion_general = data.get("puntuacion_general")
        existing.fortalezas = data.get("fortalezas")
        existing.debilidades = data.get("debilidades")
        existing.recomendacion_estrategica = data.get("recomendacion_estrategica")
        existing.siguiente_paso = data.get("siguiente_paso")
        db.commit()
        db.refresh(existing)
        return True
    row = ProjectVeredicto(
        project_id=project_id,
        decision=data.get("decision"),
        puntuacion_general=data.get("puntuacion_general"),
        fortalezas=data.get("fortalezas"),
        debilidades=data.get("debilidades"),
        recomendacion_estrategica=data.get("recomendacion_estrategica"),
        siguiente_paso=data.get("siguiente_paso"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return True


def sync_all_agent_sections(project_id: int, payload: Dict[str, Any], db: Session) -> None:
    """
    Sincroniza todas las secciones del payload del agente a sus tablas canónicas.
    Llamar después de guardar en project_agent_output (PUT o create-project).
    """
    if payload.get("estrategia_comercial"):
        sync_agent_estrategia_comercial(project_id, payload["estrategia_comercial"], db)
    if payload.get("roadmap_estrategico"):
        sync_agent_roadmap(project_id, payload["roadmap_estrategico"], db)
    if payload.get("analisis_financiero"):
        sync_agent_analisis_financiero(project_id, payload["analisis_financiero"], db)
    if payload.get("analisis_riesgos"):
        sync_agent_analisis_riesgos(project_id, payload["analisis_riesgos"], db)
    if payload.get("veredicto_final"):
        sync_agent_veredicto(project_id, payload["veredicto_final"], db)


def get_merged_sections(db: Session, project_id: int) -> Dict[str, Any]:
    """
    Devuelve los datos de cada sección desde las tablas canónicas (si existen).
    Si no hay fila canónica, el valor es None y el API usará el JSON de project_agent_output.
    """
    out: Dict[str, Any] = {
        "estrategia_comercial": None,
        "roadmap_estrategico": None,
        "analisis_financiero": None,
        "analisis_riesgos": None,
        "veredicto_final": None,
    }
    ec = db.query(ProjectEstrategiaComercial).filter(ProjectEstrategiaComercial.project_id == project_id).first()
    if ec:
        out["estrategia_comercial"] = {
            "analisis_mercado": ec.analisis_mercado,
            "estrategia_precios": ec.estrategia_precios,
            "estrategia_marketing": ec.estrategia_marketing,
            "estrategia_ventas": ec.estrategia_ventas,
        }
    rm = db.query(ProjectRoadmap).filter(ProjectRoadmap.project_id == project_id).first()
    if rm:
        out["roadmap_estrategico"] = {
            "fases": rm.fases,
            "cronograma_total_meses": rm.cronograma_total_meses,
        }
    af = db.query(ProjectAnalisisFinanciero).filter(ProjectAnalisisFinanciero.project_id == project_id).first()
    if af:
        out["analisis_financiero"] = {
            "inversion_inicial": af.inversion_inicial,
            "proyecciones_3_anos": af.proyecciones_3_anos,
            "metricas_clave": af.metricas_clave,
            "viabilidad_financiera": af.viabilidad_financiera,
        }
    ar = db.query(ProjectAnalisisRiesgos).filter(ProjectAnalisisRiesgos.project_id == project_id).first()
    riesgos = db.query(ProjectRiesgo).filter(ProjectRiesgo.project_id == project_id).order_by(ProjectRiesgo.orden).all()
    if ar or riesgos:
        out["analisis_riesgos"] = {
            "nivel_riesgo_general": ar.nivel_riesgo_general if ar else None,
            "recomendaciones": ar.recomendaciones if ar else None,
            "riesgos_identificados": [
                {"categoria": r.categoria, "riesgo": r.riesgo, "probabilidad": r.probabilidad, "impacto": r.impacto, "mitigacion": r.mitigacion}
                for r in riesgos
            ],
        }
    v = db.query(ProjectVeredicto).filter(ProjectVeredicto.project_id == project_id).first()
    if v:
        out["veredicto_final"] = {
            "decision": v.decision,
            "puntuacion_general": float(v.puntuacion_general) if v.puntuacion_general is not None else None,
            "fortalezas": v.fortalezas,
            "debilidades": v.debilidades,
            "recomendacion_estrategica": v.recomendacion_estrategica,
            "siguiente_paso": v.siguiente_paso,
        }
    return out
