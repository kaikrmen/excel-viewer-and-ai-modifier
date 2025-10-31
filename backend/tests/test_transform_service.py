from __future__ import annotations
import pandas as pd
from app.services.transform_service import (
    df_to_records,
    records_to_df,
    order_df_by_rules,
    transform_rows_local,
)

def test_local_transform_adds_expected_columns(sample_rules_dict):
    df = pd.DataFrame(
        [
            {"TIPO DE UNIDAD": "TRACTO", "Desci.": "TR", "MOD": "2022", "NO.SERIE": "AAA"},
            {"TIPO DE UNIDAD": "TANQUE", "Desci.": "TQ", "MOD": "2023", "NO.SERIE": "BBB"},
            {"TIPO DE UNIDAD": "DOLLY", "Desci.": "DL", "MOD": "2025", "NO.SERIE": "CCC"},
        ]
    )
    rows = df_to_records(df)
    enriched = transform_rows_local(sample_rules_dict, rows)
    out_df = records_to_df(enriched)
    for col in [
        "DANOS MATERIALES LIMITES",
        "DANOS MATERIALES DEDUCIBLES",
        "ROBO TOTAL LIMITES",
        "ROBO TOTAL DEDUCIBLES",
    ]:
        assert col in out_df.columns

    tracto = out_df.iloc[0]
    tanque = out_df.iloc[1]
    dolly = out_df.iloc[2]
    assert tracto["DANOS MATERIALES DEDUCIBLES"] == "10 %"
    assert tanque["ROBO TOTAL DEDUCIBLES"] == "5 %"
    assert dolly["DANOS MATERIALES DEDUCIBLES"] == "10 %"

def test_order_df_by_rules_inserts_after_no_serie(sample_rules_dict):
    df = pd.DataFrame([{"TIPO DE UNIDAD": "TRACTO", "Desci.": "X", "MOD": "2022", "NO.SERIE": "Z"}])
    rows = df_to_records(df)
    out_df = records_to_df(transform_rows_local(sample_rules_dict, rows))
    ordered = order_df_by_rules(out_df, sample_rules_dict)
    cols = list(ordered.columns)
    i_no_serie = cols.index("NO.SERIE")
    assert cols[i_no_serie + 1 : i_no_serie + 5] == [
        "DANOS MATERIALES LIMITES",
        "DANOS MATERIALES DEDUCIBLES",
        "ROBO TOTAL LIMITES",
        "ROBO TOTAL DEDUCIBLES",
    ]
