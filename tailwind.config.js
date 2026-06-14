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
    extend: {},
  },
  plugins: [],
};
