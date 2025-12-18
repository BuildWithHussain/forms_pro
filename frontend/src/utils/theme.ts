export type ThemePreferenceType = "Light" | "Dark" | "Automatic";

export default function setTheme(theme: ThemePreferenceType) {
  console.log("setTheme", theme);
  const root = document.documentElement;
  root.setAttribute("data-theme", theme.toLowerCase());
  console.log("root", root.getAttribute("data-theme"));
}
