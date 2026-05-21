
//###############################################################################################
//#####################  T E R M S  A N D  C O N D I T I O N   A D J U S T  #####################
//###############################################################################################

function pop_up_terms(){
    var popup_terms = document.getElementById('popup_terms');
    popup_terms.classList.add('active');
}

function close_terms(){
    var popup_terms = document.getElementById('popup_terms');
    popup_terms.classList.remove('active');
}