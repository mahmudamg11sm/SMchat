// PUBLIC FEED SCROLL
const feedContainer = document.getElementById("public-feed");

if(feedContainer) {
    feedContainer.scrollTop = feedContainer.scrollHeight;
}

// Example: dynamically add new post
function addPost(user, text) {
    const div = document.createElement("div");
    div.className = "post";
    div.innerHTML = `<b>${user}</b>: ${text}`;
    feedContainer.appendChild(div);
    feedContainer.scrollTop = feedContainer.scrollHeight;
}
