/* eslint-disable @typescript-eslint/no-explicit-any */
export type ParsedWorkbook = {
  file: File;
  sheetNames: string[];
  sheets: Record<string, any[][]>;
};
