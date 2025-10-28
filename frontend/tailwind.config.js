import rtlPlugin from "tailwindcss-rtl";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        surface: "#111827",
        surfaceAlt: "#131a21",
        text: "#e6edf3",
        muted: "#94a3b8",
        accent: "#22d3ee"
      }
    }
  },
  plugins: [rtlPlugin()]
};
