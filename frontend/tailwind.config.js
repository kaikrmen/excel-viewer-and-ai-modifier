/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}", "./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "var(--font-readex)",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
        },
      },
      borderRadius: { xl: "0.9rem", "2xl": "1.25rem" },
      boxShadow: {
        soft: "0 6px 16px rgba(30,64,175,0.08)",
        glow: "0 10px 40px rgba(37,99,235,0.25)",
      },
      backgroundImage: {
        "radial-dots":
          "radial-gradient(circle at 1px 1px, rgba(37,99,235,0.16) 1px, transparent 0)",
      },
      backgroundSize: {
        dots: "22px 22px",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: 0.5 },
          "50%": { opacity: 1 },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        pulseSoft: "pulseSoft 4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
