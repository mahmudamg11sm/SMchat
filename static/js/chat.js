const socket = io();

let myname = "";
let current = {
  type: "room",   // room | dm | public
  name: "General"
};

/* ================= CONNECT ================= */

socket.on("connect", () => {
  console.log("Connected");
});

/* ================= JOIN ================= */

function setMyName(name){
  myname = name;
}

/* ================= USERS ONLINE ================= */

socket.on("users_list", users=>{
  let u = document.getElementById("users");
  if(!u) return;

  u.innerHTML="";
  users.forEach(x=>{
    let d = document.createElement("div");
    d.innerText = x;
    d.onclick = ()=>openDM(x);
    u.appendChild(d);
  });
});

/* ================= TYPING ================= */

const msgInput = document.getElementById("msg");
if(msgInput){
  msgInput.addEventListener("input",()=>{
    socket.emit("typing",{
      from: myname,
      room: current.type==="room" ? current.name : null,
      to: current.type==="dm" ? current.name : null
    });
  });
}

socket.on("typing",d=>{
  if(d.from && d.from!==myname){
    let title = document.getElementById("title");
    let old = title.innerText;
    title.innerText = d.from + " is typing...";
    setTimeout(()=>title.innerText = old,1500);
  }
});

/* ================= SEND MESSAGE ================= */

function send(){
  let input = document.getElementById("msg");
  let text = input.value.trim();
  if(!text) return;

  if(current.type==="dm"){
    socket.emit("private_message",{
      to: current.name,
      msg: text
    });
  }else{
    socket.emit("room_message",{
      room: current.name,
      msg: text
    });
  }

  addMessage({
    from: myname,
    msg: text,
    me:true
  });

  input.value="";
}

/* ================= RECEIVE ================= */

socket.on("room_message",d=>{
  if(d.from !== myname && d.room===current.name){
    addMessage({from:d.from,msg:d.msg});
  }
});

socket.on("private_message",d=>{
  addMessage({from:d.from,msg:d.msg});
  socket.emit("seen",{from:d.from,to:myname});
});

/* ================= SEEN ================= */

socket.on("seen",d=>{
  addSystem(`✓✓ Seen by ${d.to}`);
});

/* ================= UI MESSAGE ================= */

function addMessage(data){
  let m=document.getElementById("messages");
  if(!m) return;

  let div=document.createElement("div");
  div.className = data.me ? "me" : "other";

  div.innerHTML = `
    <span>${data.from ? data.from+": " : ""}${data.msg}</span>
    <div class="msg-actions">
      <span onclick="likeMsg(this)">👍 <b>0</b></span>
      <span onclick="commentMsg()">💬</span>
      <span onclick="shareMsg()">🔁</span>
    </div>
  `;
  m.appendChild(div);
  m.scrollTop=m.scrollHeight;
}

function addSystem(t){
  let m=document.getElementById("messages");
  let d=document.createElement("div");
  d.className="other";
  d.innerText=t;
  m.appendChild(d);
}

/* ================= ACTIONS ================= */

function likeMsg(el){
  let b = el.querySelector("b");
  b.innerText = parseInt(b.innerText)+1;
}

function commentMsg(){
  alert("Comments feature (admin can lock/unlock)");
}

function shareMsg(){
  alert("Share coming soon");
}

/* ================= DM ================= */

function openDM(user){
  current={type:"dm",name:user};
  document.getElementById("title").innerText="DM: "+user;
  document.getElementById("messages").innerHTML="";
}

/* ================= SEARCH ================= */

function searchUser(value){
  if(!value){
    addSystem("No results");
    return;
  }
  addSystem(`Result found: ${value}`);
}

/* ================= GROUP / CHANNEL ================= */

function createGroup(name){
  socket.emit("create_room",{room:name});
}

/* ================= ONLINE STATUS ================= */

socket.on("online_users",users=>{
  document.querySelectorAll("#users div").forEach(d=>{
    d.style.color = users.includes(d.innerText) ? "#00ff88" : "#aaa";
  });
});
