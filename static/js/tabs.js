function showTab(tab) {
  document.querySelectorAll(".tab").forEach(t => {
    t.classList.remove("active");
  });

  document.querySelectorAll(".chat-item").forEach(item => {
    if (tab === "all" || item.dataset.tab === tab) {
      item.style.display = "flex";
    } else {
      item.style.display = "none";
    }
  });

  event.target.classList.add("active");
}
