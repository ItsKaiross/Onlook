//######################################################################//
//#####################  U P L O A D  C H O I C E  #####################//
//######################################################################//

var account_type_dropdown = document.getElementById('account_type_dropdowns');

var valid_id = document.getElementById('valid_id_js');
var profile_pic = document.getElementById('profile_pic_js');


account_type_dropdown.onchange = function(){
    var account_type = account_type_dropdown.value;
    if (account_type === 'citizen'){
        valid_id.style.display = "none";
        profile_pic.style.display = "none";
        valid_id.removeAttribute('required');
    }else{
        valid_id.style.display = "block";
        profile_pic.style.display = "block";
        profile_pic.removeAttribute('required');
    }
}

//######################################################################//
//#####################  P S A  F I L E  U P L O A D  ##################//
//######################################################################//

function psa_file_upload() {
    const fileInput = document.getElementById('psa_file');
    const fileInfo = document.getElementById('psa_file_info');
    const fileName = document.getElementById('psa_file_name');
    const fileSize = document.getElementById('psa_file_size');
    const viewBtn = document.getElementById('view_psa_file');
    
    if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];
        
        // Check if file is PDF
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file only.');
            fileInput.value = '';
            fileInfo.style.display = 'none';
            return;
        }
        
        // Display file information
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.style.display = 'flex';
        
        // Enable view button
        viewBtn.style.display = 'inline-block';
        viewBtn.onclick = function() {
            const fileURL = URL.createObjectURL(file);
            window.open(fileURL, '_blank');
        };
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
