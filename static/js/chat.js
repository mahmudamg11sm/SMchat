const chatBox = document.getElementById("chat-box");
const msgInput = document.getElementById("msg");
const mediaInput = document.getElementById("media");
const chatTitle = document.getElementById("chat-title");

socket.on("dm_message", d=>{
  addMessage(d.from,d.msg,d.media,d.type,d.seen);
});

socket.on("typing",d=>{
  if(d.from !== currentUser){
    const typingEl = document.getElementById("typing");
    typingEl.innerText = `${d.from} is typing...`;
    setTimeout(()=>typingEl.innerText="",1500);
  }
});

msgInput.addEventListener("input",()=>{
  socket.emit("typing",{to:chatWith});
});

function sendMsg(){
  const msg = msgInput.value;
  const file = mediaInput.files[0];

  if(file){
    const reader = new FileReader();
    reader.onload = e=>{
      socket.emit("dm_message",{to:chatWith,msg:msg,media:{name:file.name,data:Array.from(new Uint8Array(e.target.result))}});
    }
    reader.readAsArrayBuffer(file);
  }else{
    socket.emit("dm_message",{to:chatWith,msg:msg});
  }
  msgInput.value="";
  mediaInput.value="";
}

function addMessage(sender,text,media,type,seen=false){
  const div = document.createElement("div");
  div.className = sender===currentUser ? "me":"them";
  div.innerHTML = `<b>${sender}</b>: ${text} ${seen?"<span class='seen'>✓✓</span>":""}`;
  if(media){
    if(type==="image") div.innerHTML+=`<br><img src="/${media}" style="max-width:100%;border-radius:5px">`;
    if(type==="video") div.innerHTML+=`<br><video src="/${media}" controls style="max-width:100%;border-radius:5px"></video>`;
  }
  chatBox.appendChild(div);
  chatBox.scrollTop=chatBox.scrollHeight;
}
