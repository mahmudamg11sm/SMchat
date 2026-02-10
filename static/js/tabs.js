const tabs = document.querySelectorAll(".tab-btn");
const posts = document.querySelectorAll(".post");

tabs.forEach(tab=>{
  tab.onclick = () => {
    document.querySelector(".tab-btn.active").classList.remove("active");
    tab.classList.add("active");

    const type = tab.dataset.tab;

    posts.forEach(p=>{
      if(type==="all") p.style.display = "block";
      else if(type==="personal" && p.dataset.sender==="{{ current_user }}") p.style.display="block";
      else if(type==="unread" && !p.dataset.seen) p.style.display="block";
      else if(type==="public") p.style.display="block";
      else p.style.display="none";
    });
  }
});
