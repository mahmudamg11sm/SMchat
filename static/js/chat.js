// ================== SOCKET.IO ==================
const socket = io();

// ================== VARIABLES ==================
let myname = "";
let current = { type: "room", name: "General" };

// ================== ELEMENTS ==================
const usersDiv = document.getElementById("users");
const msgInput = document.getElementById("msg");
const title = document.getElementById("title");
const messages = document.getElementById("messages");

// ================== HELPERS ==================
function addMessage(text) {
  const div = document.createElement("div");
  div.className = "message";
  div.innerText = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// ================== JOIN CHAT ==================
myname = prompt("Enter your username:");
socket.emit("join", { username: myname });
socket.emit("join_room", { room: "General" });

// ================== ONLINE USERS ==================
socket.on("users_list", users => {
  usersDiv.innerHTML = "";
  users.forEach(u => {
    if (u !== myname) {
      const div = document.createElement("div");
      div.innerText = u;
      usersDiv.appendChild(div);
    }
  });
});

// ================== ONLINE COLOR ==================
socket.on("online_users", onlineUsers => {
  document.querySelectorAll("#users div").forEach(d => {
    if (onlineUsers.includes(d.innerText)) {
      d.style.color = "#FFD700"; // golden online
    } else {
      d.style.color = "#777"; // offline
    }
  });
});

// ================== CLICK ON USER (DM) ==================
usersDiv.addEventListener("click", e => {
  if (e.target.tagName === "DIV") {
    current.type = "dm";
    current.name = e.target.innerText;
    title.innerText = "DM: " + current.name;
    messages.innerHTML = "";
  }
});

// ================== SEND MESSAGE ==================
document.getElementById("send").addEventListener("click", () => {
  const text = msgInput.value.trim();
  if (!text) return;

  if (current.type === "dm") {
    socket.emit("private_message", { to: current.name, msg: text });
    addMessage(`You ➤ ${text} ✓`);
  } else {
    socket.emit("room_message", { room: current.name, msg: text });
    addMessage(`You ➤ ${text}`);
  }

  msgInput.value = "";
});

// ================== RECEIVE ROOM MESSAGE ==================
socket.on("room_message", data => {
  if (data.room === current.name) {
    addMessage(`${data.from}: ${data.msg}`);
  }
});

// ================== RECEIVE PRIVATE MESSAGE ==================
socket.on("private_message", data => {
  addMessage(`${data.from} ➤ ${data.msg} ✓`);
  // Send seen confirmation
  socket.emit("seen", { from: data.from, to: myname });
});

// ================== SEEN CONFIRMATION ==================
socket.on("seen", data => {
  addMessage(`✓✓ Seen by ${data.to}`);
});

// ================== TYPING INDICATOR ==================
msgInput.addEventListener("input", () => {
  socket.emit("typing", {
    to: current.type === "dm" ? current.name : null,
    room: current.type === "room" ? current.name : null
  });
});

socket.on("typing", data => {
  if (data.from && data.from !== myname) {
    title.innerText = `${data.from} is typing...`;
    setTimeout(() => {
      title.innerText =
        current.type === "dm"
          ? "DM: " + current.name
          : current.name || "Chat";
    }, 1500);
  }
});

// ================== CREATE / JOIN ROOM (optional) ==================
function joinRoom(roomName) {
  current.type = "room";
  current.name = roomName;
  title.innerText = roomName;
  messages.innerHTML = "";
  socket.emit("join_room", { room: roomName });
}

function createRoom(roomName) {
  socket.emit("create_room", { room: roomName });
      }
