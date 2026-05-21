var modal_add_user = document.getElementById('add-user-popup');
var add_btn = document.getElementById('add-user-btn');
var background = document.getElementById('bg-black');

add_btn.onclick = function(){
    modal_add_user.style.visibility = 'visible'
    modal_add_user.style.top = "50%"
    modal_add_user.style.transform = "translate(-50%, -50%)"
    modal_add_user.style.transition = ".5s"
    background.style.pointerEvents = "none"
    background.style.display = "block"
}

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var close_btn = document.getElementsByClassName('add-user-close')[0];

close_btn.onclick = function(){
    modal_add_user.style.visibility = "hidden";
    background.style.display = "none";
    modal_add_user.style.top = "-10%"
    modal_add_user.style.transform = "translate(-50%, -20%)"
    modal_add_user.style.transition = ".5s"
    background.style.transition = ".5s"
}


