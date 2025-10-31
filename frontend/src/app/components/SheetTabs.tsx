"use client";
import React from "react";

type Props = {
  sheets: string[];
  active: string | null;
  onChange: (name: string) => void;
};

const SheetTabs: React.FC<Props> = ({ sheets, active, onChange }) => (
  <div className="w-full overflow-x-auto">
    <div className="flex gap-2 border-b border-blue-900/40">
      {sheets.map((name) => {
        const selected = active === name;
        return (
          <button
            key={name}
            onClick={() => onChange(name)}
            className={[
              "px-4 py-2 whitespace-nowrap text-sm font-medium rounded-t-xl transition outline-none",
              selected
                ? "bg-blue-600 text-white shadow-soft border-b-2 border-blue-300"
                : "text-blue-200 hover:text-white hover:bg-blue-900/30",
            ].join(" ")}
            aria-pressed={selected}>
            {name}
          </button>
        );
      })}
    </div>
  </div>
);

export default SheetTabs;
