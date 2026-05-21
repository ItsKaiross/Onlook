var modal = document.getElementById('imageModal');
var modalImage = document.getElementById('imgModal');
var captionText = document.getElementById('caption');
var view_profile = document.getElementById('view_profile_pic');

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

//############################################################//
//#####################  V A L I D  I D  #####################//
//############################################################//

function valid_id_img(){
    const fileInput = document.getElementById('valid_id');
    const fileList = document.getElementById('valid_id_file_list');

    if (fileInput.files.length === 0){
        fileList.style.display = 'none';
        return;
    }

    fileList.innerHTML = '';
    fileList.style.display = 'block';

    Array.from(fileInput.files).forEach((file, index) => {
        if(file.size > 10e+6){
            alert(`File "${file.name}" is too big! Maximum size is 10MB.`);
            return;
        }

        const fileItem = document.createElement('div');
        fileItem.className = 'file_item';
        fileItem.innerHTML = `
            <div class="file_info">
                <span class="file_name">${file.name}</span>
                <span class="file_size">${formatFileSize(file.size)}</span>
            </div>
            <button type="button" class="view_file_btn" onclick="viewValidIdFile(${index})">VIEW</button>
        `;
        fileList.appendChild(fileItem);
    });
}

function viewValidIdFile(index) {
    const fileInput = document.getElementById('valid_id');
    if (!fileInput.files || fileInput.files.length <= index) {
        alert('File not found.');
        return;
    }
    const file = fileInput.files[index];
    const fileURL = URL.createObjectURL(file);
    
    if (file.type === 'application/pdf') {
        window.open(fileURL, '_blank');
    } else {
        modal.style.display = "block";
        modalImage.src = fileURL;
        captionText.innerHTML = file.name;
    }
}

//##################################################################//
//#####################  P R O F I L E  P I C  #####################//
//##################################################################//

function profile_img(){
    const fileInput = document.getElementById('profile_picture');
    const fileInfo = document.getElementById('profile_file_info');
    const fileName = document.getElementById('profile_file_name');
    const fileSize = document.getElementById('profile_file_size');
    const viewBtn = document.getElementById('view_profile_pic');

    if (fileInput.files.length === 0){
        return;
    }

    const file = fileInput.files[0];

    if(file.size > 10e+6){
        alert('File is too big! Maximum size is 10MB.');
        fileInput.value = '';
        fileInfo.style.display = 'none';
        return;
    }
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';
    viewBtn.style.display = 'inline-block';
}


view_profile.onclick = function(){
    const fileInput = document.getElementById('profile_picture');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please upload an image first.');
        return;
    }
    const file = fileInput.files[0];
    const fileURL = URL.createObjectURL(file);
    modal.style.display = "block";
    modalImage.src = fileURL;
    captionText.innerHTML = file.name;
}


//#######################################################//
//#####################  C L O S E  #####################//
//#######################################################//

var span = document.getElementsByClassName('close')[0];

span.onclick = function(){
    modal.style.display = "none";
}

function toggle(){
    modal.style.display = "none";
}


