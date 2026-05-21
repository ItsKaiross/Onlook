let sortDirection = {};

function filterTable() {
    const search = document.getElementById("searchInput").value.toLowerCase();
    const roleVal = document.getElementById("roleFilter").value.toLowerCase();
    const statusVal = document.getElementById("statusFilter").value.toLowerCase();

    const rows = document.querySelectorAll(".field-report-tbl tbody tr");
    let visibleCount = 0;

    rows.forEach(row => {
        const name   = row.cells[1]?.textContent.toLowerCase() || "";
        const age  = row.cells[2]?.textContent.toLowerCase() || "";

        const matchSearch = name.includes(search) || email.includes(search);
        const matchRole   = roleVal === "" || role === roleVal;
        const matchStatus = statusVal === "" || status.includes(statusVal);

        if (matchSearch && matchRole && matchStatus) {
            row.style.display = "";
            visibleCount++;
        } else {
            row.style.display = "none";
        }
    });

    // show no results message
    let noResults = document.getElementById("no-results");
    if (visibleCount === 0) {
        if (!noResults) {
            const tbody = document.querySelector(".field-report-tbl tbody");
            const tr = document.createElement("tr");
            tr.id = "no-results";
            tr.innerHTML = `<td colspan="6" class="no-results">No users found.</td>`;
            tbody.appendChild(tr);
        }
    } else {
        if (noResults) noResults.remove();
    }
}

function sortTable(colIndex) {
    const tbody = document.querySelector(".field-report-tbl tbody");
    const rows = Array.from(tbody.querySelectorAll("tr:not(#no-results)"));
    const icons = document.querySelectorAll(".sort-icon");

    // toggle direction
    sortDirection[colIndex] = sortDirection[colIndex] === "asc" ? "desc" : "asc";
    const dir = sortDirection[colIndex];

    // reset all icons
    icons.forEach(icon => {
        icon.className = "sort-icon";
        icon.textContent = "↕";
    });

    // set active icon
    const activeIcon = document.querySelectorAll(".sortable")[
        [...document.querySelectorAll(".sortable th, th.sortable")].indexOf(
            document.querySelectorAll("th.sortable")[colIndex]
        )
    ];

    // simpler icon update
    const allSortable = document.querySelectorAll("th.sortable");
    allSortable.forEach((th, i) => {
        const icon = th.querySelector(".sort-icon");
        if (i === [0,1,2].indexOf(colIndex) || th.getAttribute("onclick") === `sortTable(${colIndex})`) {
            icon.className = `sort-icon ${dir}`;
            icon.textContent = "";
        }
    });

    rows.sort((a, b) => {
        const aText = a.cells[colIndex]?.textContent.trim().toLowerCase() || "";
        const bText = b.cells[colIndex]?.textContent.trim().toLowerCase() || "";
        if (aText < bText) return dir === "asc" ? -1 : 1;
        if (aText > bText) return dir === "asc" ? 1 : -1;
        return 0;
    });

    rows.forEach(row => tbody.appendChild(row));
}