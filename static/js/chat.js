const socket = io();

let myname = prompt("Username:");
let current_channel = "General";

socket.emit("join",{username:myname,room:current_channel});

function sendMessage(){
  let msg = document.getElementById("msg").value;
  let f = document.getElementById("file").files[0];

  let media = null;
  if(f){
    let reader = new FileReader();
    reader.onload = ()=>{
      media = {name:f.name,data:Array.from(new Uint8Array(reader.result))};
      socket.emit("channel_message",{channel:current_channel,text:msg,media:media});
    };
    reader.readAsArrayBuffer(f);
  } else {
    socket.emit("channel_message",{channel:current_channel,text:msg});
  }

  document.getElementById("msg").value="";
  document.getElementById("file").value="";
}

// ---------------- RECEIVERS ----------------
socket.on("new_channel_message", d=>{
  let m = document.getElementById("messages");
  let div = document.createElement("div");
  div.className = "msg";

  let mediaHTML = "";
  if(d.type==="image") mediaHTML=`<img src="/${d.media_url}" />`;
  if(d.type==="video") mediaHTML=`<video src="/${d.media_url}" controls></video>`;

  div.innerHTML = `<b>${d.sender}</b>: ${d.text}<br>${mediaHTML}
                   <br><button onclick="like(${d.id})">Like</button>
                   <button onclick="comment(${d.id})">Comment</button>`;

  m.appendChild(div);
  m.scrollTop=m.scrollHeight;
});

socket.on("system", msg=>{
  let m = document.getElementById("messages");
  let div = document.createElement("div");
  div.style.color="yellow";
  div.innerText = msg;
  m.appendChild(div);
});
