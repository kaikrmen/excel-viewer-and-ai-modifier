from __future__ import annotations
import os
import json
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import pandas as pd

os.environ.setdefault("BACKEND_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "") 

from app.main import app  

@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture()
def api_headers():
    return {"X-API-KEY": os.environ["BACKEND_API_KEY"]}

@pytest.fixture()
def sample_rules_dict():
    return {
        "coberturas_por_tipo": {
            "TRACTOS": {
                "tipo_cobertura": "AMPLIA",
                "coberturas": {
                    "DANOS MATERIALES": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "10 %"},
                    "ROBO TOTAL": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "10 %"},
                },
            },
            "REMOLQUES": {
                "tipo_cobertura": "AMPLIA",
                "coberturas": {
                    "DANOS MATERIALES": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "5 %"},
                    "ROBO TOTAL": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "5 %"},
                },
            },
        },
        "reglas_asignacion": {
            "mapeo_columnas": {"columna_referencia": "TIPO DE UNIDAD", "columna_referencia_index": "A"},
            "columnas_a_agregar": [
                "DANOS MATERIALES LIMITES",
                "DANOS MATERIALES DEDUCIBLES",
                "ROBO TOTAL LIMITES",
                "ROBO TOTAL DEDUCIBLES",
            ],
        },
    }

@pytest.fixture()
def sample_vehicle_excel_bytes() -> BytesIO:
    # Crea un XLSX en memoria con columnas básicas
    df = pd.DataFrame(
        [
            {"TIPO DE UNIDAD": "TRACTO", "Desci.": "TR FREIGHT", "MOD": "2022", "NO.SERIE": "ABC123"},
            {"TIPO DE UNIDAD": "TANQUE", "Desci.": "RM TANQ", "MOD": "2023", "NO.SERIE": "XYZ999"},
            {"TIPO DE UNIDAD": "DOLLY", "Desci.": "DOLLY ATRO", "MOD": "2025", "NO.SERIE": "DLY001"},
        ]
    )
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="PRESENTACION 1")
    out.seek(0)
    return out

@pytest.fixture()
def coverages_sheet_bytes() -> BytesIO:
    df = pd.DataFrame(
        [
            {"coberturas": "DAÑOS MATERIALES", "LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "10%"},
            {"coberturas": "ROBO TOTAL", "LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "10%"},
        ]
    )
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="COBERTURAS")
    out.seek(0)
    return out
