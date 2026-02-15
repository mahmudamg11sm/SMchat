const socket = io();

const friend = document.querySelector(".chat-header h3").innerText;
const currentUser = document.querySelector("nav a[href^='/profile/']")?.innerText || "";
const room = [friend, currentUser].sort().join("_");

socket.emit("join_room", { room: room });

// ---------------- SEND MESSAGE ----------------
function sendMessage() {
  const input = document.getElementById("messageInput");
  const msg = input.value.trim();
  if (!msg) return;

  socket.emit("private_message", {
    to: friend,
    msg: msg
  });

  input.value = "";
}

// ---------------- RECEIVE MESSAGE ----------------
socket.on("private_message", data => {
  const box = document.getElementById("messages");

  const div = document.createElement("div");
  div.classList.add("msg");

  if (data.from === currentUser) {
    div.classList.add("me");
    div.innerHTML = `
      <span>${data.msg}</span>
      <small class="seen">${data.status}</small>
      <button onclick="deleteMessage(this)">🗑</button>
    `;
  } else {
    div.classList.add("them");
    div.innerHTML = `<span>${data.msg}</span>`;
    socket.emit("seen", { sender: data.from });
  }

  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
});

// ---------------- SEEN STATUS ----------------
socket.on("message_seen", data => {
  document.querySelectorAll(".seen").forEach(el => {
    el.innerText = "seen";
  });
});

// ---------------- USER ONLINE ----------------
socket.on("user_status", data => {
  if (data.user === friend) {
    document.getElementById("userStatus").innerText = data.status;
  }
});

// ---------------- TYPING ----------------
const input = document.getElementById("messageInput");

input.addEventListener("input", () => {
  socket.emit("typing", { to: friend });
});

socket.on("typing", data => {
  if (data.from === friend) {
    const typingDiv = document.getElementById("typing");
    typingDiv.innerText = friend + " is typing...";
    setTimeout(() => {
      typingDiv.innerText = "";
    }, 2000);
  }
});

// ---------------- DELETE MESSAGE ----------------
function deleteMessage(btn) {
  const msgDiv = btn.parentElement;
  const text = msgDiv.querySelector("span").innerText;

  socket.emit("delete_message", { text: text });
  msgDiv.remove();
}

// ---------------- VOICE RECORD ----------------
let mediaRecorder;
let audioChunks = [];

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();

      mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks);
        const reader = new FileReader();

        reader.onload = function () {
          socket.emit("voice_message", {
            to: friend,
            audio: reader.result
          });
        };

        reader.readAsDataURL(blob);
        audioChunks = [];
      };

      setTimeout(() => {
        mediaRecorder.stop();
      }, 3000);
    });
}

socket.on("voice_message", data => {
  const box = document.getElementById("messages");

  const div = document.createElement("div");
  div.classList.add("msg", "them");

  div.innerHTML = `<audio controls src="${data.audio}"></audio>`;
  box.appendChild(div);

  box.scrollTop = box.scrollHeight;
});
