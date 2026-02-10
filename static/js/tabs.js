function showTab(tab){
  const feed=document.getElementById("tabContent");
  feed.innerHTML="";
  if(tab==="all"){
    feed.innerHTML+="<div class='post'>All messages...</div>";
  }else if(tab==="personal"){
    feed.innerHTML+="<div class='post'>Personal messages...</div>";
  }else if(tab==="unread"){
    feed.innerHTML+="<div class='post'>Unread messages...</div>";
  }else if(tab==="public"){
    feed.innerHTML+="<div class='post'>Public posts...</div>";
  }
}
