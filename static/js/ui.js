let currentView = "homeView";

function openView(id){
  document.querySelectorAll(".view").forEach(v=>{
    v.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");
  currentView = id;
}

function toggleMenu(){
  document.getElementById("sideMenu").classList.toggle("show");
}

function toggleTheme(){
  document.body.classList.toggle("gold");
}
