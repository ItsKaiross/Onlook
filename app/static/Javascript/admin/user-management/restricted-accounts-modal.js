var restricted_modal = document.getElementById('restricted-accounts-popup');
var restricted_btn = document.getElementById('restricted-btn');
var background = document.getElementById('bg-black');

if (restricted_btn) {
    restricted_btn.onclick = function(){
        restricted_modal.style.visibility = 'visible'
        restricted_modal.style.top = "50%"
        restricted_modal.style.transform = "translate(-50%, -50%)"
        restricted_modal.style.transition = ".5s"
        background.style.pointerEvents = "none"
        background.style.display = "block"
        
        // Load restricted accounts data
        if (typeof loadRestrictedAccounts === 'function') {
            loadRestrictedAccounts(1, 10);
        }
    }
}

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var span = document.getElementsByClassName('restricted-close')[0];

if (span) {
    span.onclick = function(){
        restricted_modal.style.visibility = "hidden";
        background.style.display = "none";
        restricted_modal.style.top = "-10%"
        restricted_modal.style.transform = "translate(-50%, -20%)"
        restricted_modal.style.transition = ".5s"
        background.style.transition = ".5s"
    }
}