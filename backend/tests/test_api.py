from __future__ import annotations
import pandas as pd
from io import BytesIO

def test_sample_data_ok(client, api_headers):
    r = client.get("/sample-data", headers=api_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_export_with_vehicle_sheet_uses_fallback_and_returns_xlsx(
    client, api_headers, sample_vehicle_excel_bytes
):
    files = {
        "file": ("vehicles.xlsx", sample_vehicle_excel_bytes.getvalue(),
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    data = {"sheet_name": "PRESENTACION 1"}
    r = client.post("/export", headers=api_headers, files=files, data=data)
    assert r.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in r.headers["content-type"]

    xls_bytes = BytesIO(r.content)
    xl = pd.ExcelFile(xls_bytes)
    assert "PRESENTACION 1" in xl.sheet_names
    df = pd.read_excel(xl, sheet_name="PRESENTACION 1")
    for col in [
        "DANOS MATERIALES LIMITES",
        "DANOS MATERIALES DEDUCIBLES",
        "ROBO TOTAL LIMITES",
        "ROBO TOTAL DEDUCIBLES",
    ]:
        assert col in df.columns

def test_export_with_coverages_sheet_allows_empty_output(
    client, api_headers, coverages_sheet_bytes
):
    files = {
        "file": ("cov.xlsx", coverages_sheet_bytes.getvalue(),
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    data = {"sheet_name": "COBERTURAS"}
    r = client.post("/export", headers=api_headers, files=files, data=data)
    assert r.status_code == 200 
