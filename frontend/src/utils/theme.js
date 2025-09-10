export default function toggleTheme() {
	const root = document.documentElement;
	const theme = root.getAttribute("data-theme");
	root.setAttribute("data-theme", theme === "light" ? "dark" : "light");
}
