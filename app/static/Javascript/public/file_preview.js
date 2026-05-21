function previewFiles() {
    const fileInput = document.getElementById('additional_files');
    const preview = document.getElementById('file_preview');
    const viewBtn = document.getElementById('view_files_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = `View Files (${fileInput.files.length})`;
        
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            fileDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer;';
            fileDiv.onclick = () => openFileModal(file);

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
                fileDiv.appendChild(img);
            } else {
                const icon = document.createElement('div');
                icon.textContent = file.type.includes('pdf') ? '📄' : '📝';
                icon.style.cssText = 'font-size: 50px; text-align: center;';
                fileDiv.appendChild(icon);
            }

            const fileName = document.createElement('p');
            fileName.textContent = file.name;
            fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center;';
            fileDiv.appendChild(fileName);

            preview.appendChild(fileDiv);
        }
    } else {
        viewBtn.style.display = 'none';
    }
}

function previewAdditionalImages() {
    const fileInput = document.getElementById('additional_images');
    const preview = document.getElementById('additional_images_preview');
    const viewBtn = document.getElementById('view_additional_images_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = `View Images (${fileInput.files.length})`;
        
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            
            // Only process image files
            if (file.type.startsWith('image/')) {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'image-item';
                imageDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer; position: relative;';
                imageDiv.onclick = () => openImageModal(file);

                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
                imageDiv.appendChild(img);

                const fileName = document.createElement('p');
                fileName.textContent = file.name;
                fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center; word-break: break-word;';
                imageDiv.appendChild(fileName);

                const fileSize = document.createElement('p');
                fileSize.textContent = `${(file.size/1024/1024).toFixed(2)} MB`;
                fileSize.style.cssText = 'margin: 0; font-size: 10px; text-align: center; color: #666;';
                imageDiv.appendChild(fileSize);

                preview.appendChild(imageDiv);
            }
        }
    } else {
        viewBtn.style.display = 'none';
    }
}

function toggleAdditionalImagesPreview() {
    const preview = document.getElementById('additional_images_preview');
    const btn = document.getElementById('view_additional_images_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function previewAdditionalImages() {
    const fileInput = document.getElementById('additional_images');
    const preview = document.getElementById('additional_images_preview');
    const viewBtn = document.getElementById('view_additional_images_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = `View Images (${fileInput.files.length})`;
        
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            
            // Only process image files
            if (file.type.startsWith('image/')) {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'image-item';
                imageDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer; position: relative;';
                imageDiv.onclick = () => openImageModal(file);

                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
                imageDiv.appendChild(img);

                const fileName = document.createElement('p');
                fileName.textContent = file.name;
                fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center; word-break: break-word;';
                imageDiv.appendChild(fileName);

                const fileSize = document.createElement('p');
                fileSize.textContent = `${(file.size/1024/1024).toFixed(2)} MB`;
                fileSize.style.cssText = 'margin: 0; font-size: 10px; text-align: center; color: #666;';
                imageDiv.appendChild(fileSize);

                preview.appendChild(imageDiv);
            }
        }
    } else {
        viewBtn.style.display = 'none';
    }
}

function toggleAdditionalImagesPreview() {
    const preview = document.getElementById('additional_images_preview');
    const btn = document.getElementById('view_additional_images_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function previewHelpAdditionalImages() {
    const fileInput = document.getElementById('help_additional_images');
    const preview = document.getElementById('help_additional_images_preview');
    const viewBtn = document.getElementById('help_view_additional_images_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = `View Images (${fileInput.files.length})`;
        
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            
            // Only process image files
            if (file.type.startsWith('image/')) {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'image-item';
                imageDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer; position: relative;';
                imageDiv.onclick = () => openImageModal(file);

                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
                imageDiv.appendChild(img);

                const fileName = document.createElement('p');
                fileName.textContent = file.name;
                fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center; word-break: break-word;';
                imageDiv.appendChild(fileName);

                const fileSize = document.createElement('p');
                fileSize.textContent = `${(file.size/1024/1024).toFixed(2)} MB`;
                fileSize.style.cssText = 'margin: 0; font-size: 10px; text-align: center; color: #666;';
                imageDiv.appendChild(fileSize);

                preview.appendChild(imageDiv);
            }
        }
    } else {
        viewBtn.style.display = 'none';
    }
}

function toggleHelpAdditionalImagesPreview() {
    const preview = document.getElementById('help_additional_images_preview');
    const btn = document.getElementById('help_view_additional_images_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function toggleFilePreview() {
    const preview = document.getElementById('file_preview');
    const btn = document.getElementById('view_files_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function openFileModal(file) {
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center;';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };

    const closeBtn = document.createElement('div');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = 'position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; cursor: pointer; z-index: 10001;';
    closeBtn.onclick = () => modal.remove();
    modal.appendChild(closeBtn);

    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.cssText = 'max-width: 90%; max-height: 90%; border-radius: 10px;';
        modal.appendChild(img);
    } else {
        const fileInfo = document.createElement('div');
        fileInfo.style.cssText = 'background: white; padding: 30px; border-radius: 10px; text-align: center; position: relative;';
        fileInfo.innerHTML = `<h3>${file.name}</h3><p>File type: ${file.type}</p><p>Size: ${(file.size/1024/1024).toFixed(2)} MB</p>`;
        modal.appendChild(fileInfo);
    }

    document.body.appendChild(modal);
}