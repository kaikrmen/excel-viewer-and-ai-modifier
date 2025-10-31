from __future__ import annotations
from app.services.rules_utils import get_ref_col, get_coberturas_por_tipo

def test_get_ref_col_default(sample_rules_dict):
    assert get_ref_col(sample_rules_dict) == "TIPO DE UNIDAD"

def test_get_coberturas_por_tipo(sample_rules_dict):
    cpt = get_coberturas_por_tipo(sample_rules_dict)
    assert "TRACTOS" in cpt and "REMOLQUES" in cpt
    assert "DANOS MATERIALES" in cpt["TRACTOS"]["coberturas"]
