from __future__ import annotations
import os
import time
import random
from typing import List, Dict, Any
import orjson
from openai import OpenAI

from ..core.config import settings
from .rules_utils import get_ref_col, get_coberturas_por_tipo  

Row = Dict[str, Any]
Rules = Dict[str, Any]


def _dumps(obj: Any) -> str:
    return orjson.dumps(obj, option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS).decode()


class LLMClient:
    """
    Enrich rows using a real OpenAI model if OPENAI_API_KEY is set.
    Uses Chat Completions (response_format=json_object) to force strict JSON.
    Falls back to deterministic rules if anything fails.
    """

    def __init__(self) -> None:
        self.api_key = (getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")).strip()
        self.model   = (getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")).strip()

        base_url_from_settings = (getattr(settings, "OPENAI_BASE_URL", None) or "") or ""
        base_url_from_env = os.getenv("OPENAI_BASE_URL", "") or ""
        base_url = (base_url_from_settings or base_url_from_env or "").strip() or None

        self.enabled = bool(self.api_key)
        self.client = OpenAI(api_key=self.api_key, base_url=base_url) if self.enabled else None

        self.expected_new_cols = [
            "DANOS MATERIALES LIMITES",
            "DANOS MATERIALES DEDUCIBLES",
            "ROBO TOTAL LIMITES",
            "ROBO TOTAL DEDUCIBLES",
        ]
        self.last_used_llm: bool = False  

    # -------------------- Public API --------------------
    def transform_rows(self, rules: Rules, rows: List[Row]) -> List[Row]:
        if not rows:
            self.last_used_llm = False
            return rows

        if not self.enabled:
            self.last_used_llm = False
            return self._fallback_transform(rules, rows)

        try:
            batch_size = 40
            enriched: List[Row] = []
            for i in range(0, len(rows), batch_size):
                chunk = rows[i : i + batch_size]
                if not chunk:
                    continue
                enriched.extend(self._transform_chunk_with_llm(rules, chunk))
            self.last_used_llm = True
            return enriched
        except Exception as e:
            print(f"[LLM] Error: {e!r} -> using deterministic fallback")
            self.last_used_llm = False
            return self._fallback_transform(rules, rows)

    # -------------------- Internals --------------------
    def _with_retries(self, fn, tries: int = 3):
        """
        Retry simple para redes/ratelimits del LLM.
        """
        last = None
        for k in range(tries):
            try:
                return fn()
            except Exception as e:
                last = e
                time.sleep(0.5 + random.random())
        raise last

    def _build_llm_payload(self, rules: Rules, rows: List[Row]) -> dict:
        compact_rows = [{"idx": i, **r} for i, r in enumerate(rows)]
        return {
            "rules": {
                "coberturas_por_tipo": get_coberturas_por_tipo(rules),
                "reglas_asignacion": {
                    "mapeo_columnas": {"columna_referencia": get_ref_col(rules, "TIPO DE UNIDAD")}
                },
            },
            "rows": compact_rows,
            "reference_column": get_ref_col(rules, "TIPO DE UNIDAD"),
            "expected_new_cols": self.expected_new_cols,
        }

    def _transform_chunk_with_llm(self, rules: Rules, rows: List[Row]) -> List[Row]:
        assert self.client is not None
        if not rows:
            return []

        system = (
            "You are an underwriting enrichment assistant for fleet insurance.\n"
            "Given JSON 'rules' and 'rows', you must return STRICT JSON (object) with this shape:\n"
            '{ "rows": [ { "idx": number, '
            '"DANOS MATERIALES LIMITES": string, '
            '"DANOS MATERIALES DEDUCIBLES": string, '
            '"ROBO TOTAL LIMITES": string, '
            '"ROBO TOTAL DEDUCIBLES": string } ... ] }\n'
            "If a rule does not apply for a row, use empty string for those fields.\n"
            "Return ONLY valid JSON. No extra commentary."
        )

        compact_rows_original = [{"idx": i, **r} for i, r in enumerate(rows)]
        payload_original = {
            "rules": rules,
            "rows": compact_rows_original,
            "reference_column": (
                rules.get("reglas_asignacion", {})
                .get("mapeo_columnas", {})
                .get("columna_referencia", "TIPO DE UNIDAD")
            ),
            "expected_new_cols": self.expected_new_cols,
        }
        payload = self._build_llm_payload(rules, rows)
        try:
            _ = _dumps(payload)
        except Exception:
            payload = payload_original
        

        def _call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": _dumps(payload)},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

        chat = self._with_retries(_call, tries=3)
        text = (chat.choices[0].message.content or "").strip()

        try:
            data = orjson.loads(text)
            if not isinstance(data, dict) or "rows" not in data or not isinstance(data["rows"], list):
                raise ValueError("Model did not return an object with 'rows' array.")
            rows_out = data["rows"]
        except Exception as e:
            print(f"[LLM] JSON parse error: {e!r}")
            return self._fallback_transform(rules, rows)

        merged: List[Row] = []
        for i, row in enumerate(rows):
            found = next((o for o in rows_out if isinstance(o, dict) and o.get("idx") == i), {})
            out_row = dict(row)
            for col in self.expected_new_cols:
                out_row[col] = str(found.get(col, "") or "")
            merged.append(out_row)
        return merged

    def _fallback_transform(self, rules: Rules, rows: List[Row]) -> List[Row]:
        coberturas = rules.get("coberturas_por_tipo", {})
        columna_ref = (
            rules.get("reglas_asignacion", {})
            .get("mapeo_columnas", {})
            .get("columna_referencia", "TIPO DE UNIDAD")
        )

        out: List[Row] = []
        for row in rows:
            unidad = str(row.get(columna_ref, "")).upper()
            tipo = None
            if "TRACTO" in unidad:
                tipo = "TRACTOS"
            elif "REMOLQUE" in unidad or "TANQUE" in unidad:
                tipo = "REMOLQUES"
            elif "DOLLY" in unidad:
                tipo = "TRACTOS"

            merged = dict(row)
            if tipo and tipo in coberturas:
                cov = coberturas[tipo].get("coberturas", {}) or {}
                danos = cov.get("DANOS MATERIALES", {}) or {}
                robo  = cov.get("ROBO TOTAL", {}) or {}

                merged["DANOS MATERIALES LIMITES"] = danos.get("LIMITES", "")
                merged["DANOS MATERIALES DEDUCIBLES"] = danos.get("DEDUCIBLES", "")
                merged["ROBO TOTAL LIMITES"] = robo.get("LIMITES", "")
                merged["ROBO TOTAL DEDUCIBLES"] = robo.get("DEDUCIBLES", "")
            else:
                for col in self.expected_new_cols:
                    merged[col] = ""
            out.append(merged)
        return out
