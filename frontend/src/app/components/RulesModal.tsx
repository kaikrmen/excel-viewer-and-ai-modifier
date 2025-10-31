/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import React, { useEffect, useMemo } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { X, Download, Copy } from "lucide-react";

type Props = {
  open: boolean;
  onClose: () => void;
  rules: any | null;
};

function ExplainRules({ rules }: { rules: any }) {
  if (!rules || typeof rules !== "object") return null;

  const coverByType = rules?.coberturas_por_tipo || {};
  const assign = rules?.reglas_asignacion || {};
  const finalStruct = rules?.estructura_excel_final || {};

  const refCol = assign?.mapeo_columnas?.columna_referencia || "TIPO DE UNIDAD";
  const columnsToAdd: string[] = assign?.columnas_a_agregar || [];

  const mapRows = (obj: any) =>
    Object.entries(obj || {}).map(([k, v]) => ({ key: k, val: v as any }));

  return (
    <div className="space-y-5 text-sm text-blue-100/90">
      <h3 className="text-base font-semibold text-blue-100">
        What these rules do
      </h3>

      {/* 1) Coverage by Unit Type */}
      <div className="rounded-lg border border-blue-900/40 bg-blue-950/40 p-3">
        <p className="font-medium text-blue-200 mb-1">
          1) Coverage templates per unit type
        </p>
        <p className="opacity-90">
          <strong>Purpose:</strong> Define default insurance coverage per unit
          category (e.g. <em>TRACTOS</em>, <em>REMOLQUES</em>). Each category
          specifies <em>tipo_cobertura</em> and per-coverage limits/deductibles.
        </p>
        <div className="mt-3 space-y-3">
          {mapRows(coverByType).map(({ key, val }) => (
            <div key={key} className="rounded-md border border-blue-900/30 p-2">
              <div className="text-blue-200 font-medium">{key}</div>
              {"tipo_cobertura" in (val || {}) && (
                <div className="text-xs opacity-80">
                  Coverage type: <code>{val.tipo_cobertura}</code>
                </div>
              )}
              {val?.coberturas && (
                <ul className="mt-2 text-xs grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {Object.entries(val.coberturas).map(([cKey, cVal]: any) => (
                    <li
                      key={cKey}
                      className="rounded bg-blue-950/40 p-2 border border-blue-900/30">
                      <div className="font-semibold text-blue-100">{cKey}</div>
                      <div>
                        LIMITES: <code>{cVal?.LIMITES ?? ""}</code>
                      </div>
                      <div>
                        DEDUCIBLES: <code>{cVal?.DEDUCIBLES ?? ""}</code>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 2) Assignment rules */}
      <div className="rounded-lg border border-blue-900/40 bg-blue-950/40 p-3">
        <p className="font-medium text-blue-200 mb-1">
          2) Assignment & new columns
        </p>
        <p className="opacity-90">
          <strong>Purpose:</strong> For each row, look at <code>{refCol}</code>{" "}
          and add the following columns with values taken from the coverage
          template of the matching unit type.
        </p>
        {columnsToAdd.length > 0 && (
          <ul className="list-disc pl-5 mt-2 opacity-90">
            {columnsToAdd.map((c) => (
              <li key={c}>
                <code>{c}</code>
              </li>
            ))}
          </ul>
        )}
        {assign?.descripcion && (
          <p className="opacity-70 mt-2 text-xs">Note: {assign.descripcion}</p>
        )}
      </div>

      {/* 3) Final Excel structure */}
      <div className="rounded-lg border border-blue-900/40 bg-blue-950/40 p-3">
        <p className="font-medium text-blue-200 mb-1">
          3) Final Excel structure
        </p>
        <p className="opacity-90">
          <strong>Purpose:</strong> Keep column order and insert the new fields
          specifically after <code>NO.SERIE</code> (column D).
        </p>
        {Array.isArray(finalStruct?.columnas_finales) && (
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-1 mt-2 text-xs opacity-90">
            {finalStruct.columnas_finales.map((c: string) => (
              <li
                key={c}
                className="rounded border border-blue-900/30 bg-blue-950/30 p-2">
                {c}
              </li>
            ))}
          </ul>
        )}
        {Array.isArray(finalStruct?.notas) && (
          <ul className="list-disc pl-5 mt-2 text-xs opacity-80">
            {finalStruct.notas.map((n: string, i: number) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function RulesModal({ open, onClose, rules }: Props) {
  // lock scroll while open
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  // portal container (body)
  const portalTarget = useMemo(
    () => (typeof window !== "undefined" ? document.body : null),
    []
  );

  if (!portalTarget) return null;

  const jsonPretty =
    rules && typeof rules === "object"
      ? JSON.stringify(rules, null, 2)
      : String(rules ?? "{}");

  const copyJSON = async () => {
    try {
      await navigator.clipboard.writeText(jsonPretty);
    } catch {}
  };

  const downloadJSON = () => {
    const blob = new Blob([jsonPretty], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "enrichment_rules.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return createPortal(
    <AnimatePresence>
      {open && (
        <motion.div
          role="dialog"
          aria-modal="true"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[120] flex items-center justify-center">
          {/* Backdrop (cubre todo, evita ver el hero) */}
          <motion.div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Modal card */}
          <motion.div
            initial={{ y: 28, scale: 0.98, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            exit={{ y: 16, scale: 0.98, opacity: 0 }}
            transition={{ type: "spring", stiffness: 230, damping: 24 }}
            className="relative z-[121] w-[min(1000px,95vw)] max-h-[85vh] overflow-hidden rounded-2xl border border-blue-900/60 bg-[#0b1220] shadow-2xl">
            {/* Header */}
            <div className="flex items-start justify-between gap-4 border-b border-blue-900/50 p-5">
              <div className="pr-2">
                <h2 className="text-xl font-semibold text-blue-100">
                  Enrichment Rules
                </h2>
                <p className="text-xs text-blue-300/85">
                  These rules drive the AI enrichment: add default insurance
                  fields by unit type, normalize text columns, and compute
                  derived metrics used for underwriting.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={copyJSON}
                  className="rounded-lg px-3 py-2 text-blue-100 hover:bg-blue-900/40 transition"
                  title="Copy JSON"
                  aria-label="Copy JSON">
                  <Copy className="size-4" />
                </button>
                <button
                  onClick={downloadJSON}
                  className="rounded-lg px-3 py-2 text-blue-100 hover:bg-blue-900/40 transition"
                  title="Download JSON"
                  aria-label="Download JSON">
                  <Download className="size-4" />
                </button>
                <button
                  onClick={onClose}
                  className="rounded-lg p-2 text-blue-100 hover:bg-blue-900/40 transition"
                  aria-label="Close modal"
                  title="Close">
                  <X className="size-5" />
                </button>
              </div>
            </div>

            {/* Body: grid responsive con scroll interno */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-5 max-h-[calc(85vh-7.5rem)] overflow-auto">
              {/* JSON */}
              <div className="order-2 lg:order-1 overflow-auto rounded-xl border border-blue-900/50 bg-blue-950/40 p-3">
                <pre className="text-[12px] leading-relaxed text-blue-100 font-mono">
                  {jsonPretty}
                </pre>
              </div>

              {/* Explicación */}
              <div className="order-1 lg:order-2">
                <ExplainRules rules={rules} />
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-2 border-t border-blue-900/50 p-4">
              <button
                onClick={onClose}
                className="rounded-xl border border-blue-900/60 px-4 py-2 text-blue-100 hover:bg-blue-900/40 transition">
                Close
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    portalTarget
  );
}
