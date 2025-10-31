/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useMemo, useState, useEffect } from "react";
import * as XLSX from "xlsx";
import type { ParsedWorkbook } from "@/types";
import { apiGet, apiPost } from "@/lib/api";

import { Github } from "lucide-react";
import Hero from "./components/Hero";
import RulesButton from "./components/RulesButton";
import SheetTabs from "./components/SheetTabs";
import DataTable from "./components/DataTable";

export default function Page() {
  const [wb, setWb] = useState<ParsedWorkbook | null>(null);
  const [activeSheet, setActiveSheet] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [csrf, setCsrf] = useState<string>("");

  useEffect(() => {
    apiGet("/csrf")
      .then(({ csrf }) => setCsrf(csrf))
      .catch(() => {});
  }, []);

  const activeData = useMemo(
    () => (!wb || !activeSheet ? null : wb.sheets[activeSheet] ?? null),
    [wb, activeSheet]
  );

  const onUpload = async (file: File) => {
    setError(null);
    const buf = await file.arrayBuffer();
    const workbook = XLSX.read(buf, {
      type: "array",
      cellDates: false,
      cellText: false,
    });
    const sheetNames = workbook.SheetNames;

    const sheets: Record<string, any[][]> = {};
    sheetNames.forEach((name) => {
      const ws = workbook.Sheets[name];
      const aoa = XLSX.utils.sheet_to_json(ws, {
        header: 1,
        blankrows: true,
        defval: "",
        raw: false,
      }) as any[][];
      sheets[name] = aoa;
    });

    setWb({ file, sheetNames, sheets });
    setActiveSheet(sheetNames[0] ?? null);
  };

  const onExport = async () => {
    if (!wb || !activeSheet || !csrf) return;
    setIsLoading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append("file", wb.file);
      fd.append("sheet_name", activeSheet);

      const res = await apiPost("/export", fd, csrf);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `modified_${wb.file.name}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.message ?? "Unexpected error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-6xl p-6 flex flex-col gap-6">
      <Hero />

      <section id="uploader" className="card p-8 mt-8">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold text-blue-200">
            Upload Excel file (.xlsx)
          </h2>
          <RulesButton />
        </div>

        <input
          type="file"
          accept=".xlsx"
          onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
          className="mt-3 w-full border border-blue-700 bg-slate-800 text-sm rounded-lg p-3"
        />

        {!wb?.sheetNames?.length && (
          <p className="mt-4 text-blue-300/70 text-sm">No file uploaded yet.</p>
        )}

        {wb?.sheetNames?.length ? (
          <div className="mt-6">
            <SheetTabs
              sheets={wb.sheetNames}
              active={activeSheet}
              onChange={setActiveSheet}
            />
            <div className="mt-4 flex justify-between items-center">
              <p className="text-blue-300/70 text-sm">
                Active sheet:{" "}
                <span className="font-semibold text-blue-400">
                  {activeSheet}
                </span>
              </p>
              <button
                className="btn-primary"
                disabled={isLoading}
                onClick={onExport}>
                {isLoading ? "Exporting..." : "Export Modified Excel"}
              </button>
            </div>

            <div className="mt-4">
              <DataTable data={activeData ?? []} />
            </div>

            {error && <p className="text-sm text-red-400 mt-3">{error}</p>}
          </div>
        ) : null}
      </section>

      <footer className="mt-10 text-sm text-blue-300 flex flex-col items-center gap-2 py-6 border-t border-blue-900/50">
        <p>Built with Next.js · Tailwind · SheetJS · FastAPI · OpenAI</p>
        <a
          href="https://github.com/kaikrmen"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 text-blue-200 hover:text-blue-400 transition">
          <Github className="size-5" />
          <span>
            Made by <strong>Carmen Cecilia</strong> — @kaikrmen
          </span>
        </a>
      </footer>
    </main>
  );
}
