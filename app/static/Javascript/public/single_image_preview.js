function previewLastSeenImage() {
    const fileInput = document.getElementById('upload_last_seen');
    const preview = document.getElementById('last_seen_preview');
    const viewBtn = document.getElementById('view_last_seen_btn');
    
    preview.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = 'View Image (1)';
        
        const file = fileInput.files[0];
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer;';
        fileDiv.onclick = () => openFileModal(file);

        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px;';
        fileDiv.appendChild(img);

        const fileName = document.createElement('p');
        fileName.textContent = file.name;
        fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center;';
        fileDiv.appendChild(fileName);

        preview.appendChild(fileDiv);
    } else {
        viewBtn.style.display = 'none';
    }
}

function previewLastSeenImage2() {
    const fileInput = document.getElementById('upload_last_seen2');
    const preview = document.getElementById('last_seen_preview2');
    const viewBtn = document.getElementById('view_last_seen_btn2');
    
    if (!fileInput || !preview || !viewBtn) {
        console.error('Required elements not found for image preview');
        return;
    }
    
    preview.innerHTML = '';
    
    if (fileInput.files && fileInput.files.length > 0) {
        viewBtn.style.display = 'block';
        viewBtn.textContent = 'View Image (1)';
        
        const file = fileInput.files[0];
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select a valid image file.');
            fileInput.value = '';
            viewBtn.style.display = 'none';
            return;
        }
        
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.style.cssText = 'margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: inline-block; cursor: pointer;';
        fileDiv.onclick = () => openFileModal(file);

        const img = document.createElement('img');
        img.onload = function() {
            URL.revokeObjectURL(this.src); // Clean up memory
        };
        img.onerror = function() {
            console.error('Failed to load image preview');
            fileDiv.innerHTML = '<p style="color: red;">Failed to load image</p>';
        };
        img.src = URL.createObjectURL(file);
        img.style.cssText = 'width: 100px; height: 100px; object-fit: cover; border-radius: 5px; display: block;';
        img.alt = 'Image preview';
        fileDiv.appendChild(img);

        const fileName = document.createElement('p');
        fileName.textContent = file.name;
        fileName.style.cssText = 'margin: 5px 0; font-size: 12px; text-align: center; word-break: break-all;';
        fileDiv.appendChild(fileName);

        preview.appendChild(fileDiv);
        
        // Show preview by default
        preview.style.display = 'block';
    } else {
        viewBtn.style.display = 'none';
        preview.style.display = 'none';
    }
}

function toggleLastSeenPreview() {
    const preview = document.getElementById('last_seen_preview');
    const btn = document.getElementById('view_last_seen_btn');
    
    if (preview.style.display === 'none') {
        preview.style.display = 'block';
        btn.textContent = btn.textContent.replace('View', 'Hide');
    } else {
        preview.style.display = 'none';
        btn.textContent = btn.textContent.replace('Hide', 'View');
    }
}

function toggleLastSeenPreview2() {
    const preview = document.getElementById('last_seen_preview2');
    const btn = document.getElementById('view_last_seen_btn2');
    
    if (!preview || !btn) {
        console.error('Preview elements not found');
        return;
    }
    
    const isHidden = preview.style.display === 'none' || preview.style.display === '';
    
    if (isHidden) {
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

    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.style.cssText = 'max-width: 90%; max-height: 90%; border-radius: 10px;';
    modal.appendChild(img);

    // Add escape key listener
    const escapeHandler = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);

    document.body.appendChild(modal);
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.style.display = 'none';
    }
}