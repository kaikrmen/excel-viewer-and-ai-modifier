/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import React, { useState } from "react";
import { apiGet } from "@/lib/api";
import RulesModal from "./RulesModal";

export default function RulesButton() {
  const [open, setOpen] = useState(false);
  const [rules, setRules] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const onClick = async () => {
    try {
      setLoading(true);
      const data = await apiGet("/sample-data");
      setRules(data);
      setOpen(true);
    } catch (e: any) {
      alert(e?.message || "Unknown error fetching rules");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={onClick}
        disabled={loading}
        className="btn-ghost border border-blue-900/50 hover:bg-white/10 rounded-xl px-3 py-2 text-blue-200 disabled:opacity-60">
        {loading ? "Loading..." : "View Rules"}
      </button>

      <RulesModal open={open} onClose={() => setOpen(false)} rules={rules} />
    </>
  );
}
