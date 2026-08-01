/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{njk,html,md,js}",
  ],
  safelist: [
    "active", "hidden", "visible",
    "text-gray-500", "text-gray-700",
    "bg-white", "bg-transparent",
    "rotate-180",
  ],
  theme: {
    extend: {
      colors: {
        // Site-wide readability fix.
        // gray-400/500 are used throughout as muted BODY copy on white and on
        // --surf. Tailwind's defaults measure 2.54:1 and 4.83:1 against white,
        // so the 400 ramp failed WCAG AA everywhere it was used. These are
        // re-pointed at the brand's cool-neutral ramp, which keeps the same
        // "muted" look while clearing 4.5:1.
        // 200/300 are left untouched — they are only used on dark surfaces,
        // where lighter is what we want.
        gray: {
          400: "#5A6883", // was #9CA3AF (2.54:1) -> 5.61:1 on white
          500: "#4C5A75", // was #6B7280 (4.83:1) -> 6.94:1 on white
        },
      },
    },
  },
  plugins: [],
};
