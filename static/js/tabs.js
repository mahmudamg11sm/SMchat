// ALL / PERSONAL / UNREAD / PUBLIC TABS
const tabs = document.querySelectorAll(".top-tabs div");
const views = document.querySelectorAll(".tab-view");

tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");

        const target = tab.dataset.target;
        views.forEach(v => v.style.display = v.id===target ? "block" : "none");
    });
});
