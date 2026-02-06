const socket = io();
let myname = "";
let current = {type:"room", name:"General"};

function join(){
  myname = document.getElementById("username").value;
  if(!myname) return alert("Enter username");
  socket.emit("join",{username:myname});
  document.getElementById("login").style.display="none";
  document.getElementById("chat").style.display="block";
  socket.emit("join_room",{room:"General"});
}

// Users list
socket.on("users_list", users=>{
  let u = document.getElementById("users");
  u.innerHTML="";
  users.forEach(x=>{
    if(x!==myname) u.innerHTML += `<div onclick="dm('${x}')">${x}</div>`;
  });
});

// Rooms list
socket.on("rooms_list", rooms=>{
  let r = document.getElementById("rooms");
  r.innerHTML="";
  rooms.forEach(x=> r.innerHTML += `<div onclick="joinRoom('${x}')">${x}</div>`);
});

// DM
function dm(u){
  current={type:"dm",name:u};
  document.getElementById("title").innerText="DM: "+u;
  document.getElementById("messages").innerHTML="";
}

// Join group
function joinRoom(r){
  current={type:"room",name:r};
  socket.emit("join_room",{room:r});
  document.getElementById("title").innerText=r;
  document.getElementById("messages").innerHTML="";
}

// Create room
function createRoom(){
  let r=document.getElementById("newRoom").value;
  if(!r) return;
  socket.emit("create_room",{room:r});
}

// Send message
function send(){
  let m=document.getElementById("msg").value;
  if(!m) return;
  if(current.type==="dm") socket.emit("private_message",{to:current.name,msg:m});
  else socket.emit("room_message",{room:current.name,msg:m});
  document.getElementById("msg").value="";
}

// Receive messages
socket.on("private_message",d=> add(`${d.from}: ${d.msg}`));
socket.on("room_message",d=> {if(d.room===current.name) add(`${d.from}: ${d.msg}`);});

// Seen
socket.on("seen",d=> add(`✓✓ Seen by ${d.to}`));

function add(t){
  let m=document.getElementById("messages");
  let div=document.createElement("div");
  div.innerText=t;
  div.className="message";
  m.appendChild(div);
  m.scrollTop=m.scrollHeight;
}

// Media upload
function sendMedia(){
  let f = document.getElementById("mediaFile").files[0];
  if(!f) return;
  let reader = new FileReader();
  reader.onload = function(e){
    socket.emit("media_message",{
      file:{
        name:f.name,
        data:Array.from(new Uint8Array(e.target.result))
      },
      room: current.name
    });
  }
  reader.readAsArrayBuffer(f);
}

// Receive media
socket.on("media_message",d=>{
  let m=document.getElementById("messages");
  let div=document.createElement("div");
  div.className="message";
  if(d.type==="image") div.innerHTML = `<b>${d.from}</b><br><img src="/${d.url}" style="max-width:100%;border-radius:10px">`;
  if(d.type==="video") div.innerHTML = `<b>${d.from}</b><br><video src="/${d.url}" controls style="max-width:100%;border-radius:10px"></video>`;
  m.appendChild(div);
  m.scrollTop=m.scrollHeight;
});
