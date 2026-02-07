const socket = io();
let myname = "{{ username }}";

function sendMessage(){
  const msg = document.getElementById("msg").value;
  socket.emit("channel_message", {channel:"General", text:msg});
  document.getElementById("msg").value="";
}

socket.on("new_channel_message", d=>{
  const m = document.getElementById("messages");
  let div = document.createElement("div");
  div.className = "message";
  let badges = "";
  if(d.sender==="admin"){ badges += '<span class="badge admin">ADMIN</span>'; }
  if(d.sender==="verified"){ badges += '<span class="badge verified">✔</span>'; }
  if(d.type==="text"){
    div.innerHTML = `<b>${d.sender}</b>${badges}: ${d.text}`;
  }
  if(d.type==="image"){
    div.innerHTML = `<b>${d.sender}</b>${badges}: <img src="/${d.media_url}" class="media">`;
  }
  if(d.type==="video"){
    div.innerHTML = `<b>${d.sender}</b>${badges}: <video src="/${d.media_url}" controls class="media"></video>`;
  }
  m.appendChild(div);
  m.scrollTop = m.scrollHeight;
});

function switchView(v){
  document.querySelectorAll(".view").forEach(x=>x.classList.remove("active"));
  document.getElementById("view-"+v).classList.add("active");
}
