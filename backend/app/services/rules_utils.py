from __future__ import annotations
from typing import Any, Dict

Rules = Dict[str, Any]

def get_section_top_or_nested(rules: Rules, key: str) -> Dict[str, Any]:
    sec = rules.get(key)
    if isinstance(sec, dict):
        return sec
    cpt = rules.get("coberturas_por_tipo")
    if isinstance(cpt, dict):
        nested = cpt.get(key)
        if isinstance(nested, dict):
            return nested
    return {}

def get_reglas_asignacion(rules: Rules) -> Dict[str, Any]:
    return get_section_top_or_nested(rules, "reglas_asignacion")

def get_ref_col(rules: Rules, default: str = "TIPO DE UNIDAD") -> str:
    ra = get_reglas_asignacion(rules)
    return (
        ra.get("mapeo_columnas", {}).get("columna_referencia")
        or default
    )

def get_coberturas_por_tipo(rules: Rules) -> Dict[str, Any]:
    cpt = rules.get("coberturas_por_tipo")
    return cpt if isinstance(cpt, dict) else {}
