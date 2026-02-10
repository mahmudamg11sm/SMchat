const input = document.querySelector(".chat-form input");
const typing = document.getElementById("typing");
let timer;

input.addEventListener("input", () => {
  typing.style.display = "block";
  clearTimeout(timer);
  timer = setTimeout(() => {
    typing.style.display = "none";
  }, 1000);
});
