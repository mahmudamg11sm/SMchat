const socket = io();
const chatBox = document.getElementById("chat-box");
const msgInput = document.getElementById("msg");
const chatForm = document.getElementById("chat-form");
const mediaInput = document.getElementById("media");
let typingTimeout;

chatForm.addEventListener("submit", e => {
  e.preventDefault();
  sendMessage();
});

msgInput.addEventListener("input", () => {
  socket.emit("typing", { to: "{{ username }}" });
});

socket.on("typing", d => {
  const typingDiv = document.getElementById("typing");
  typingDiv.innerText = `${d.from} is typing...`;
  clearTimeout(typingTimeout);
  typingTimeout = setTimeout(() => { typingDiv.innerText = ""; }, 1500);
});

socket.on("private_message", d => {
  addMessage(d.from, d.msg, d.type, d.seen, d.from=== "{{ current_user }}");
});

function sendMessage() {
  const msg = msgInput.value;
  const media = mediaInput.files[0];

  if (media) {
    const reader = new FileReader();
    reader.onload = function() {
      socket.emit("media_message", {
        to: "{{ username }}",
        file: { name: media.name, data: Array.from(new Uint8Array(this.result)) },
        room: "{{ username }}",
      });
    };
    reader.readAsArrayBuffer(media);
    mediaInput.value = "";
  }

  if (msg.trim()!=="") {
    socket.emit("private_message", { to: "{{ username }}", msg });
    msgInput.value = "";
  }
}

function addMessage(from, text, type="text", seen=false, isMe=false) {
  const div = document.createElement("div");
  div.className = isMe ? "me" : "them";

  let content = `<span class="sender">${from}</span>: `;
  if (type==="text") content += text;
  if (type==="image") content += `<img src="/static/uploads/images/${text}">`;
  if (type==="video") content += `<video src="/static/uploads/videos/${text}" controls></video>`;
  if (seen) content += `<span class="seen">✓✓</span>`;

  div.innerHTML = content;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
          }
