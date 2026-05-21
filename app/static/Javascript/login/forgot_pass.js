//#############################################################################
//#####################  F O R G O T  P A S S  P O P U P  #####################
//#############################################################################

function openForgotPasswordPopup() {
    const popup = document.getElementById('popup_forgot_pass');
    const bgBlack = document.getElementById('bg-black');
    
    popup.classList.add('active');
    bgBlack.classList.add('active');
}

function closeForgotPasswordPopup() {
    const popup = document.getElementById('popup_forgot_pass');
    const bgBlack = document.getElementById('bg-black');
    
    popup.classList.remove('active');
    bgBlack.classList.remove('active');
}

function toggle(){
    var blur = document.getElementById('blur');
    var popup_forgot_pass = document.getElementById('popup_forgot_pass');
    var bgBlack = document.getElementById('bg-black');

    blur.classList.toggle('active');
    popup_forgot_pass.classList.toggle('active');
    bgBlack.classList.toggle('active');
}
