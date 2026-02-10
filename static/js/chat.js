// SOCKET.IO CHAT
const socket = io();
const msgInput = document.getElementById("msg");
const messages = document.getElementById("messages");
const typingIndicator = document.getElementById("typing");

let currentChatUser = null; // set on click to DM

msgInput?.addEventListener("input", () => {
    if(!currentChatUser) return;
    socket.emit("typing", { to: currentChatUser });
});

function sendMessage() {
    if(!currentChatUser) return;
    const text = msgInput.value.trim();
    if(!text) return;
    socket.emit("private_message", { to: currentChatUser, msg: text });
    msgInput.value = "";
}

// RECEIVE MESSAGE
socket.on("private_message", data => {
    const div = document.createElement("div");
    div.className = data.from === currentChatUser ? "them" : "me";

    if(data.type==="text"){
        div.innerHTML = `<b>${data.from}</b>: ${data.msg} <span class="seen">✓✓</span>`;
    }

    if(data.type==="image"){
        div.innerHTML = `<b>${data.from}</b><br><img src="/${data.media_url}" style="max-width:100%;border-radius:10px">`;
    }

    if(data.type==="video"){
        div.innerHTML = `<b>${data.from}</b><br><video src="/${data.media_url}" controls style="max-width:100%;border-radius:10px"></video>`;
    }

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
});

// TYPING INDICATOR
socket.on("typing", d => {
    if(d.from === currentChatUser){
        typingIndicator.style.display = "block";
        typingIndicator.innerText = `${d.from} is typing...`;
        setTimeout(()=>{ typingIndicator.style.display="none"; },1500);
    }
});
