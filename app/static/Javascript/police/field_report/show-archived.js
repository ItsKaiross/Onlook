let showingArchived = false;

function toggleArchived() {
    showingArchived = !showingArchived;
    const params = new URLSearchParams(window.location.search);
    params.set('field_page', 1);

    if (showingArchived) {
        params.set('status', 'Archived');
    } else {
        params.delete('status');
    }

    window.location.href = '?' + params.toString();
}

// on page load — highlight button if status=Archived is in URL
document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    const btn = document.getElementById("toggle-archived-btn");

    if (params.get("status") === "Archived") {
        showingArchived = true;
        btn.textContent = "View Active";
        btn.classList.add("active");
    }
});