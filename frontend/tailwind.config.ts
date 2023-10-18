import type { Config } from "tailwindcss";

const config: Config = {
  purge: {
    options: {
      safelist: [
        'bg-yellow-300',
        'bg-gray-300',
        'bg-gray-400',
        'bg-zinc-300',
        'bg-zinc-400',
        'bg-red-300',
        'bg-green-300',
        'bg-cyan-300',
        'bg-fuchsia-300',
        'bg-yellow-400',
        'bg-green-400',
        'bg-cyan-400',
        'bg-fuchsia-400',
        'bg-red-400',
        // ... any other dynamically constructed classes
      ],
    },
  },
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    screens: {
      sm: '100px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    },
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
