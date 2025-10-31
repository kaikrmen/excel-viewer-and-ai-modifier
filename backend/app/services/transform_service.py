from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import re
import unicodedata

SPANISH_NEW_COLS = [
    "DANOS MATERIALES LIMITES",
    "DANOS MATERIALES DEDUCIBLES",
    "ROBO TOTAL LIMITES",
    "ROBO TOTAL DEDUCIBLES",
]

def df_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    return df.fillna("").astype(str).to_dict(orient="records")

def records_to_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame.from_records(rows)
    return df.fillna("").astype(str)

def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

def _norm(s: str) -> str:
    s = (s or "").strip()
    s = _strip_accents(s)
    s = re.sub(r"\s+", " ", s)
    return s.upper()

def _contains_any(text: str, terms: List[str]) -> bool:
    T = _norm(text)
    return any(t in T for t in map(_norm, terms))

_TRACTO_TERMS   = ["TRACTO", "TRACTOCAMION", "TRACTOCAMI0N", "TR TR", "TR FREIGH", "TRACTOR"]
_REMOLQUE_TERMS = ["REMOLQUE", "TANQUE", "TANQUERO", "RM", "RM TANQ", "REM", "SEMI"]
_DOLLY_TERMS    = ["DOLLY"]

def classify_unit(unit_raw: str) -> str:
    u = _norm(unit_raw)
    if any(u.startswith(_norm(x)) or _norm(x) in u for x in _TRACTO_TERMS):
        return "TRACTOS"
    if any(u.startswith(_norm(x)) or _norm(x) in u for x in _REMOLQUE_TERMS):
        return "REMOLQUES"
    if any(u.startswith(_norm(x)) or _norm(x) in u for x in _DOLLY_TERMS):
        return "TRACTOS"
    return u

def looks_like_spanish_rules(rules: Dict[str, Any]) -> bool:
    return (
        isinstance(rules, dict)
        and "coberturas_por_tipo" in rules
        and "reglas_asignacion" in rules
    )

def enrich_spanish_rules(row: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row)
    ref_col = (
        rules.get("reglas_asignacion", {})
             .get("mapeo_columnas", {})
             .get("columna_referencia", "TIPO DE UNIDAD")
    )
    unit_val = row.get(ref_col, "")
    group_key = classify_unit(str(unit_val))

    cover_by_type = rules.get("coberturas_por_tipo", {})
    tpl = cover_by_type.get(group_key)

    danos_lim = danos_ded = robo_lim = robo_ded = ""

    if tpl and isinstance(tpl.get("coberturas"), dict):
        danos = tpl["coberturas"].get("DANOS MATERIALES") or {}
        robo  = tpl["coberturas"].get("ROBO TOTAL") or {}
        danos_lim = danos.get("LIMITES", "") or ""
        danos_ded = danos.get("DEDUCIBLES", "") or ""
        robo_lim  = robo.get("LIMITES", "") or ""
        robo_ded  = robo.get("DEDUCIBLES", "") or ""

    out["DANOS MATERIALES LIMITES"]    = danos_lim
    out["DANOS MATERIALES DEDUCIBLES"] = danos_ded
    out["ROBO TOTAL LIMITES"]          = robo_lim
    out["ROBO TOTAL DEDUCIBLES"]       = robo_ded

    return out

def transform_rows_local(rules: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if looks_like_spanish_rules(rules):
        return [enrich_spanish_rules(r, rules) for r in rows]
    return rows

_BASE_MATCHES = {
    "TIPO DE UNIDAD": ["TIPO DE UNIDAD", "TIPO DE U", "TIPO U", "UNIDAD"],
    "Desci.":        ["DESCI.", "DESCI", "DESCRIPCION", "DESCRIPCIÓN", "DESC."],
    "MOD":           ["MOD", "MODELO", "AÑO", "ANIO"],
    "NO.SERIE":      ["NO.SERIE", "NO SERIE", "NO. SERIE", "NUM SERIE", "NUM. SERIE", "NRO SERIE"],
}

def _resolve_column(existing: List[str], aliases: List[str]) -> Optional[str]:
    ex_norm = { _norm(c): c for c in existing }
    for a in aliases:
        key = _norm(a)
        if key in ex_norm:
            return ex_norm[key]
    for a in aliases:
        key = _norm(a)
        for e_norm, original in ex_norm.items():
            if key in e_norm:
                return original
    return None

def _ensure_new_cols(df: pd.DataFrame, new_cols: List[str]) -> pd.DataFrame:
    for c in new_cols:
        if c not in df.columns:
            df[c] = ""
    return df

def order_df_by_rules(df: pd.DataFrame, rules: Dict[str, Any]) -> pd.DataFrame:
    if df.empty:
        return df

    existing = list(df.columns)

    serie_col = _resolve_column(existing, _BASE_MATCHES["NO.SERIE"])

    df = _ensure_new_cols(df, SPANISH_NEW_COLS)

    if not serie_col:
        return df 

    cols = list(df.columns)
    idx = cols.index(serie_col)

    left  = cols[: idx + 1]
    news  = [c for c in SPANISH_NEW_COLS if c in cols]
    right = [c for c in cols if c not in left and c not in news]

    ordered = left + news + right
    return df.reindex(columns=ordered)
