import type { Metadata } from "next";
import { Readex_Pro } from "next/font/google";
import "./globals.css";

const readex = Readex_Pro({
  subsets: ["latin"],
  variable: "--font-readex",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Excel Viewer & AI Modifier",
  description: "Upload, preview, and export AI-enriched Excel files",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={readex.variable}>
      <body className="min-h-screen font-sans antialiased">{children}</body>
    </html>
  );
}
