var modal_waccount_reported_missing_public = document.getElementById('reported-missing-waccount-popup');
var add_btn = document.getElementById('reported-missing-waccount-btn');
var background = document.getElementById('bg-black');

if (add_btn) {
    add_btn.onclick = function(){
    modal_waccount_reported_missing_public.style.visibility = 'visible'
    modal_waccount_reported_missing_public.style.top = "50%"
    modal_waccount_reported_missing_public.style.transform = "translate(-50%, -50%)"
    modal_waccount_reported_missing_public.style.transition = ".5s"
    modal_waccount_reported_missing_public.classList.add('show'); // Add show class for arrows
    background.style.pointerEvents = "none"
    background.style.display = "block"
    }
}

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var close_btn = document.getElementsByClassName('reported-missing-waccount-close')[0];

if (close_btn) {
    close_btn.onclick = function(){
    modal_waccount_reported_missing_public.style.visibility = "hidden";
    modal_waccount_reported_missing_public.classList.remove('show'); // Remove show class to hide arrows
    background.style.display = "none";
    modal_waccount_reported_missing_public.style.top = "-10%"
    modal_waccount_reported_missing_public.style.transform = "translate(-50%, -20%)"
    modal_waccount_reported_missing_public.style.transition = ".5s"
    background.style.transition = ".5s"
    }
}
