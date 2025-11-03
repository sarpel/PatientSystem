/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        medical: {
          primary: "#3b82f6",
          secondary: "#60a5fa",
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          critical: "#dc2626",
        },
      },
    },
  },
  plugins: [],
};
