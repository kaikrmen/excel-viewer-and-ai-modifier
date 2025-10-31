/* eslint-disable @typescript-eslint/no-explicit-any */
// app/(site)/components/DataTable.tsx
"use client";
import React from "react";

type AOA = any[][];

function isAllEmpty(row: any[]): boolean {
  return !row || row.every((c) => String(c ?? "").trim() === "");
}

function tidyAoA(data: AOA): AOA {
  if (!data || data.length === 0) return [];
  const rows = data.filter((r) => !isAllEmpty(r));
  if (rows.length === 0) return [];
  let maxCol = 0;
  rows.forEach((r) => {
    for (let i = r.length - 1; i >= 0; i--) {
      if (String(r[i] ?? "").trim() !== "") {
        if (i > maxCol) maxCol = i;
        break;
      }
    }
  });
  return rows.map((r) => r.slice(0, maxCol + 1));
}

const HEADER_HINTS = [
  "TIPO",
  "TIPO DE UNIDAD",
  "DESCI",
  "MOD",
  "NO.SERIE",
  "COBERTURAS",
  "LÍMITES",
  "LIMITES",
  "DEDUCIBLES",
].map((s) => s.toUpperCase());

function detectHeaderIndex(rows: AOA): number | null {
  const up = (x: any) => String(x ?? "").toUpperCase();
  for (let i = 0; i < Math.min(rows.length, 20); i++) {
    const joined = rows[i].map(up).join(" ");
    if (HEADER_HINTS.some((h) => joined.includes(h))) return i;
  }
  return null;
}

function formatCell(value: any): string {
  if (value === null || value === undefined) return "";

  const str = String(value).trim();

  if (!str) return "";

  const num = Number(str.replace(",", "."));
  if (!isNaN(num)) {
    if (num > 0 && num <= 1) return `${(num * 100).toFixed(0)}%`;
    if (num > 1_000 && num % 1 === 0) return num.toLocaleString("es-ES");
  }

  if (/^n\/?a$/i.test(str)) return "N/A";

  if (str.startsWith("$")) return str.replace(/\s/g, "");

  if (/^\d{5,}$/.test(str)) return Number(str).toLocaleString("es-ES");

  return str;
}

const DataTable: React.FC<{ data: AOA }> = ({ data }) => {
  const clean = tidyAoA(data);
  if (!clean.length) {
    return <p className="text-sm text-blue-300/70">No data to display.</p>;
  }

  const headerIdx = detectHeaderIndex(clean);
  const hasHeader = headerIdx !== null;

  const header = hasHeader
    ? clean[headerIdx!]
    : clean[0].map((_: unknown, i: number) => `Column ${i + 1}`);

  const body = hasHeader ? clean.slice(headerIdx! + 1) : clean.slice(1);

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-blue-900/40 bg-[#0d1420] shadow-soft">
      <table className="min-w-[720px] w-full">
        <thead className="bg-blue-900/50 sticky top-0">
          <tr>
            {header.map((h: any, i: number) => (
              <th
                key={i}
                className="px-3 py-2 text-left text-xs font-semibold text-blue-100 border-b border-blue-900/50">
                {String(h ?? "")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row: any[], rIdx: number) => (
            <tr
              key={rIdx}
              className="odd:bg-transparent even:bg-blue-900/10 hover:bg-blue-900/20 transition">
              {header.map((_: any, cIdx: number) => (
                <td
                  key={cIdx}
                  className="px-3 py-2 text-sm text-blue-100/90 border-b border-blue-900/40">
                  {formatCell(row?.[cIdx])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
