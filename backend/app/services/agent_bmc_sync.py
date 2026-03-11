"""
Sincroniza el BMC que viene en la salida del agente (JSON) con la tabla business_model_canvases.
La tabla business_model_canvases es la fuente única de verdad para visualización y edición del BMC.
"""
import json
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from ..models.business_model_canvas import BusinessModelCanvas


def _to_json_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    return json.dumps([val], ensure_ascii=False) if val else None


def sync_agent_bmc_to_canvas(project_id: int, bmc_data: Dict[str, Any], db: Session) -> bool:
    """
    Crea o actualiza el registro en business_model_canvases a partir del JSON
    del agente (business_model_canvas de salidaAgente.json).
    Devuelve True si se creó o actualizó el BMC.
    """
    if not bmc_data:
        return False

    key_partners = bmc_data.get("alianzas_clave")
    key_activities = bmc_data.get("actividades_clave")
    key_resources = bmc_data.get("recursos_clave")
    if isinstance(key_resources, dict):
        all_r = (
            (key_resources.get("tecnologicos") or [])
            + (key_resources.get("humanos") or [])
            + (key_resources.get("financieros") or [])
        )
        key_resources = all_r

    value_propositions = bmc_data.get("propuesta_valor")
    if isinstance(value_propositions, dict):
        value_propositions = value_propositions.get("beneficios_clave") or (
            [value_propositions["descripcion"]] if value_propositions.get("descripcion") else []
        )
    if isinstance(value_propositions, str):
        value_propositions = [value_propositions]

    customer_relationships = bmc_data.get("relacion_clientes")
    if isinstance(customer_relationships, dict):
        customer_relationships = customer_relationships.get("estrategias") or [
            customer_relationships.get("tipo", "")
        ]

    channels = bmc_data.get("canales")
    if isinstance(channels, dict):
        channels = (channels.get("distribucion") or []) + (channels.get("comunicacion") or [])

    customer_segments = bmc_data.get("segmentos_clientes")
    if isinstance(customer_segments, dict):
        customer_segments = customer_segments.get("detalles") or [
            customer_segments.get("descripcion", "")
        ]

    cost_structure = bmc_data.get("estructura_costos")
    if isinstance(cost_structure, dict):
        cf = cost_structure.get("costos_fijos") or []
        cv = cost_structure.get("costos_variables") or []
        cost_structure = [str(x) for x in cf] + [str(x) for x in cv]

    revenue_streams = bmc_data.get("fuentes_ingresos")
    if isinstance(revenue_streams, dict):
        precios = revenue_streams.get("precios") or []
        revenue_streams = (
            [
                f"{x.get('plan', '')}: {x.get('precio', '')} {x.get('moneda', '')}"
                for x in precios
            ]
            if precios
            else [revenue_streams.get("modelo", "")]
        )

    existing = (
        db.query(BusinessModelCanvas)
        .filter(BusinessModelCanvas.project_id == project_id)
        .first()
    )
    if existing:
        existing.key_partners = _to_json_str(key_partners)
        existing.key_activities = _to_json_str(key_activities)
        existing.key_resources = _to_json_str(key_resources)
        existing.value_propositions = _to_json_str(value_propositions)
        existing.customer_relationships = _to_json_str(customer_relationships)
        existing.channels = _to_json_str(channels)
        existing.customer_segments = _to_json_str(customer_segments)
        existing.cost_structure = _to_json_str(cost_structure)
        existing.revenue_streams = _to_json_str(revenue_streams)
        db.commit()
        db.refresh(existing)
        return True

    bmc = BusinessModelCanvas(
        project_id=project_id,
        key_partners=_to_json_str(key_partners),
        key_activities=_to_json_str(key_activities),
        key_resources=_to_json_str(key_resources),
        value_propositions=_to_json_str(value_propositions),
        customer_relationships=_to_json_str(customer_relationships),
        channels=_to_json_str(channels),
        customer_segments=_to_json_str(customer_segments),
        cost_structure=_to_json_str(cost_structure),
        revenue_streams=_to_json_str(revenue_streams),
    )
    db.add(bmc)
    db.commit()
    db.refresh(bmc)
    return True
