document.querySelectorAll(".tabs a").forEach(tab => {
  tab.addEventListener("click", e => {
    e.preventDefault();
    const target = tab.dataset.tab;

    document.querySelectorAll(".tab-view").forEach(v => {
      v.style.display = "none";
    });

    if (target) {
      document.getElementById(target).style.display = "block";
    }
  });
});
