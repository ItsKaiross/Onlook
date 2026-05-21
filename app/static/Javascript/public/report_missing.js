var modal_report_missing_public = document.getElementById('report-missing-popup');
var add_btn = document.getElementById('report-missing');
var background = document.getElementById('bg-black');

if (add_btn) {
    add_btn.onclick = function(){
    modal_report_missing_public.style.visibility = 'visible'
    modal_report_missing_public.style.top = "50%"
    modal_report_missing_public.style.transform = "translate(-50%, -50%)"
    modal_report_missing_public.style.transition = ".5s"
    background.style.pointerEvents = "none"
    background.style.display = "block"
    
    // Initialize map when popup opens
    setTimeout(function() {
        if (typeof initPopupMap === 'function') {
            initPopupMap();
        }
    }, 500);
    }
}

//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//




//##################### W A C C  #####################//

var close_wacc_btn1 = document.getElementsByClassName('w-noacc-missing-report-close')[0];
var close_wacc_btn2 = document.getElementsByClassName('w-noacc-missing-report-close2')[0];
var close_wacc_btn3 = document.getElementsByClassName('w-noacc-missing-report-close3')[0];
var close_wacc_btn4 = document.getElementsByClassName('w-noacc-missing-report-close4')[0];
var close_wacc_btn5 = document.getElementsByClassName('w-noacc-missing-report-close5')[0];




if (close_wacc_btn1) {
    close_wacc_btn1.onclick = function(){
    modal_report_missing_public.style.visibility = "hidden";
    background.style.display = "none";
    modal_report_missing_public.style.top = "-10%"
    modal_report_missing_public.style.transform = "translate(-50%, -20%)"
    modal_report_missing_public.style.transition = ".5s"
    background.style.transition = ".5s"
}

}

if (close_wacc_btn2) {
    close_wacc_btn2.onclick = function(){
    modal_report_missing_public.style.visibility = "hidden";
    background.style.display = "none";
    modal_report_missing_public.style.top = "-10%"
    modal_report_missing_public.style.transform = "translate(-50%, -20%)"
    modal_report_missing_public.style.transition = ".5s"
    background.style.transition = ".5s"
}

}

if (close_wacc_btn3) {
    close_wacc_btn3.onclick = function(){
    modal_report_missing_public.style.visibility = "hidden";
    background.style.display = "none";
    modal_report_missing_public.style.top = "-10%"
    modal_report_missing_public.style.transform = "translate(-50%, -20%)"
    modal_report_missing_public.style.transition = ".5s"
    background.style.transition = ".5s"
}

}

if (close_wacc_btn4) {
    close_wacc_btn4.onclick = function(){
    modal_report_missing_public.style.visibility = "hidden";
    background.style.display = "none";
    modal_report_missing_public.style.top = "-10%"
    modal_report_missing_public.style.transform = "translate(-50%, -20%)"
    modal_report_missing_public.style.transition = ".5s"
    background.style.transition = ".5s"
}

}

if (close_wacc_btn5) {
    close_wacc_btn5.onclick = function(){
    modal_report_missing_public.style.visibility = "hidden";
    background.style.display = "none";
    modal_report_missing_public.style.top = "-10%"
    modal_report_missing_public.style.transform = "translate(-50%, -20%)"
    modal_report_missing_public.style.transition = ".5s"
    background.style.transition = ".5s"
    }
}



