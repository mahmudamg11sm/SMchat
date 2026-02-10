document.querySelectorAll(".like-btn").forEach(btn=>{
  btn.onclick = () => {
    const postDiv = btn.closest(".post");
    const postId = postDiv.dataset.id;
    socket.emit("like_post",{id:postId});
  }
});

document.querySelectorAll(".comment-btn").forEach(btn=>{
  btn.onclick = () => {
    const postDiv = btn.closest(".post");
    const commentsDiv = postDiv.querySelector(".comments");
    commentsDiv.style.display = commentsDiv.style.display==="none" ? "block" : "none";
  }
});

document.querySelectorAll(".comment-input").forEach(input=>{
  input.addEventListener("keypress", e=>{
    if(e.key==="Enter"){
      const postDiv = input.closest(".post");
      const postId = postDiv.dataset.id;
      socket.emit("comment_post",{id:postId,text:input.value});
      input.value="";
    }
  });
});

socket.on("update_post", data=>{
  const postDiv = document.querySelector(`.post[data-id='${data.id}']`);
  if(postDiv){
    postDiv.querySelector(".like-btn").innerText = `Like (${data.likes})`;
    const commentsDiv = postDiv.querySelector(".comments");
    commentsDiv.innerHTML = "";
    data.comments.forEach(c=>{
      const div = document.createElement("div");
      div.innerHTML = `<b>${c.commenter}</b>: ${c.text}`;
      commentsDiv.appendChild(div);
    });
  }
});
