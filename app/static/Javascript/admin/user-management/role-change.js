let pendingTransfer = null;

function updateRole(selectEl){
    const id = selectEl.dataset.id;
    const value = selectEl.value;
    const roleEl = document.getElementById("user-" + id);

    if (value === "systemAdmin"){
        pendingTransfer = {selectEl, id, value};
        document.getElementById("transferModal").style.display = "flex";
        return;
    }

    saveRole(selectEl, id, value, roleEl);
}

function confirmTransfer(){
    document.getElementById("transferModal").style.display = "none";
    if(!pendingTransfer) return;

    const {selectEl, id, value} = pendingTransfer;
    const roleEl = document.getElementById("user-" + id);
    pendingTransfer = null;

    saveRole(selectEl, id, value, roleEl, true);
}

function cancelTransfer(){
    document.getElementById("transferModal").style.display = "none";
    if (pendingTransfer) location.reload();
    pendingTransfer = null;
}

function saveRole(selectEl, id, value, roleEl, logoutAfter = false){

    selectEl.disabled = true;
    roleEl.textContent = "Saving...";
    roleEl.className = "saving";


    fetch ("/update-roles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id, value: value})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            selectEl.disabled = false;
            roleEl.textContent = "Saved ✓";
            roleEl.className = "saved";
            
            if(logoutAfter){
                setTimeout(() => window.location.href = "/logout", 1500);
            } else {
                setTimeout(() => roleEl.textContent = "", 2000);
            }

        }
    })
    .catch(() => {
        selectEl.disabled = false;
        roleEl.textContent = "Error!";
        roleEl.className = "error";
    })
}