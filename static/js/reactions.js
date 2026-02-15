const socket = io();

// SEND REACTION
function sendReaction(emoji, postId) {
  socket.emit("reaction", {
    emoji: emoji,
    post_id: postId
  });
}

// RECEIVE REACTION
socket.on("reaction", data => {
  const post = document.querySelector(`.post[data-id='${data.post_id}']`);
  if (!post) return;

  let countSpan = post.querySelector(".reaction-count");

  if (!countSpan) {
    countSpan = document.createElement("span");
    countSpan.classList.add("reaction-count");
    post.querySelector(".reactions").appendChild(countSpan);
  }

  countSpan.innerText = `${data.emoji} +1`;
});
