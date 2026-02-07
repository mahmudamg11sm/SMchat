const socket = io();

let myName = prompt("Enter username");
let currentChannel = "General";

socket.emit("join", { username: myName, room: currentChannel });

const messages = document.getElementById("messages");

function addMessage(html){
  let div = document.createElement("div");
  div.className = "message";
  div.innerHTML = html;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function sendMessage(){
  let text = document.getElementById("msgInput").value;
  let fileInput = document.getElementById("mediaInput");

  if(fileInput.files.length > 0){
    let file = fileInput.files[0];
    let reader = new FileReader();

    reader.onload = ()=>{
      socket.emit("channel_message",{
        channel: currentChannel,
        text: text,
        media: {
          name: file.name,
          data: Array.from(new Uint8Array(reader.result))
        }
      });
    };
    reader.readAsArrayBuffer(file);
    fileInput.value = "";
  }else{
    socket.emit("channel_message",{
      channel: currentChannel,
      text: text
    });
  }

  document.getElementById("msgInput").value = "";
}

socket.on("new_channel_message", d=>{
  if(d.type === "image"){
    addMessage(`<b>${d.sender}</b><br><img src="/${d.media_url}">`);
  }else if(d.type === "video"){
    addMessage(`<b>${d.sender}</b><br><video controls src="/${d.media_url}"></video>`);
  }else{
    addMessage(`<b>${d.sender}</b>: ${d.text}`);
  }
});

socket.on("system", msg=>{
  addMessage(`<i>${msg}</i>`);
});

socket.on("users_list", users=>{
  let u = document.getElementById("users");
  u.innerHTML = "";
  users.forEach(x=>{
    let d = document.createElement("div");
    d.innerText = x;
    d.onclick = ()=>{
      openView("chatView");
      document.getElementById("chatTitle").innerText = x;
    };
    u.appendChild(d);
  });
});
