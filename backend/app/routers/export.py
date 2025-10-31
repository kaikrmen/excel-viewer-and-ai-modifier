from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from ..core.security import require_api_key
from ..services.llm_service import LLMClient
from ..services.transform_service import (
    df_to_records,
    records_to_df,
    order_df_by_rules,
)

from io import BytesIO
from pathlib import Path
import pandas as pd
import json
import re
from typing import List, Optional

router = APIRouter()
DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample_test3.json"

# -------------------------------
# Helpers
# -------------------------------
def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().upper())

def _row_has_any_value(row: pd.Series) -> bool:
    return any(str(v).strip() != "" for v in row.tolist())

def _count_nonempty(row: pd.Series) -> int:
    return sum(1 for v in row.tolist() if str(v).strip() != "")

def _is_header_row(row: pd.Series, hints: List[str], need: int | None = None) -> bool:
    vals = [str(v) for v in row.tolist()]
    J = _norm(" ".join(vals))
    need = need or max(1, len(hints) - 1)
    hits = sum(1 for h in hints if _norm(h) in J)
    return hits >= need

def _read_excel_loose_table(raw: pd.DataFrame, min_cols: int = 2) -> pd.DataFrame:
    header_idx: Optional[int] = None
    for i in range(min(len(raw), 40)):
        if _count_nonempty(raw.iloc[i]) >= min_cols:
            header_idx = i
            break
    if header_idx is None:
        return pd.DataFrame()

    headers = raw.iloc[header_idx].fillna("").astype(str).tolist()
    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df.columns = headers

    def _bad_name(c: str) -> bool:
        C = (c or "").strip()
        return (not C) or C.upper().startswith("UNNAMED")
    df = df.loc[:, [not _bad_name(c) for c in df.columns]]

    df = df.fillna("").astype(str)
    df = df[~df.apply(lambda r: all((str(v).strip() == "") for v in r), axis=1)].reset_index(drop=True)
    return df

def _read_excel_smart(xls: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
    raw = pd.read_excel(xls, sheet_name=sheet_name, dtype=str, header=None)
    if raw.empty:
        return raw

    SN = _norm(sheet_name)

    if "COBERTURAS" in SN:
        header_hints_sets = [
            ["COBERTURAS", "LIMITES", "DEDUCIBLES"],
            ["COBERTURAS", "LÍMITES", "DEDUCIBLES"],
        ]
        need_hits = 2  # 2 de 3
    else:
        header_hints_sets = [
            ["TIPO", "NO.SERIE"],
            ["TIPO DE UNIDAD", "NO.SERIE"],
            ["TIPO", "MOD", "NO.SERIE"],
        ]
        need_hits = None

    header_idx = None
    for i in range(min(len(raw), 40)):
        row = raw.iloc[i]
        if not _row_has_any_value(row):
            continue
        for hints in header_hints_sets:
            if _is_header_row(row, hints, need=need_hits):
                header_idx = i
                break
        if header_idx is not None:
            break

    if header_idx is None:
        return _read_excel_loose_table(raw, min_cols=2)

    header_values = raw.iloc[header_idx].fillna("").astype(str).tolist()
    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df.columns = header_values

    def _bad_name(c: str) -> bool:
        C = (c or "").strip()
        return (not C) or C.upper().startswith("UNNAMED")
    df = df.loc[:, [not _bad_name(c) for c in df.columns]]

    df = df.fillna("").astype(str)
    df = df[~df.apply(lambda r: all((str(v).strip() == "") for v in r), axis=1)].reset_index(drop=True)
    return df

def load_rules() -> dict | None:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def _stream_df(df: pd.DataFrame, original_filename: str, sheet_name: str) -> StreamingResponse:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="modified_{original_filename}"'}
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

# -------------------------------
# Routes
# -------------------------------
@router.get("/sample-data", dependencies=[Depends(require_api_key)])
def sample_data():
    rules = load_rules()
    if rules is None:
        return JSONResponse({"message": "No rules file found on server."}, status_code=200)
    return rules

@router.post("/export", dependencies=[Depends(require_api_key)])
async def export_excel(
    file: UploadFile = File(..., description="Original .xlsx"),
    sheet_name: str = Form(..., description="Sheet to transform"),
):
    try:
        content = await file.read()
        xls = pd.ExcelFile(BytesIO(content))
        if sheet_name not in xls.sheet_names:
            return JSONResponse(
                {"error": f"Sheet '{sheet_name}' not found. Available: {xls.sheet_names}"},
                status_code=400,
            )

        df = _read_excel_smart(xls, sheet_name=sheet_name)

        if "COBERTURAS" in _norm(sheet_name):
            return _stream_df(df, file.filename, sheet_name)

        if df.empty:
            return _stream_df(pd.DataFrame(), file.filename, sheet_name)

        rules = load_rules() or {}

        ref_col = (
            rules.get("reglas_asignacion", {})
                 .get("mapeo_columnas", {})
                 .get("columna_referencia", "TIPO DE UNIDAD")
        )

        if ref_col in df.columns:
            rows = df_to_records(df)
            llm = LLMClient()
            transformed_rows = llm.transform_rows(rules=rules, rows=rows)
            out_df = records_to_df(transformed_rows)
            out_df.columns = [str(c) for c in out_df.columns]
            out_df = order_df_by_rules(out_df, rules)
        else:
            out_df = df

        return _stream_df(out_df, file.filename, sheet_name)

    except Exception as e:
        return JSONResponse({"error": f"Export failed: {e!r}"}, status_code=500)
