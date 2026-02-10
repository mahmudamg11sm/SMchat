// DARK / GOLD TOGGLE
const body = document.body;

document.getElementById("darkBtn")?.addEventListener("click", () => {
    body.classList.remove("gold");
    body.classList.toggle("dark");
});

document.getElementById("goldBtn")?.addEventListener("click", () => {
    body.classList.remove("dark");
    body.classList.toggle("gold");
});
