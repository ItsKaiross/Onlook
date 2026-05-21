document.addEventListener("DOMContentLoaded", function() {
    const fieldSelect = document.getElementById("field-report-rows-per-page");
    const caseSelect = document.getElementById("case-management-rows-per-page");

    if (fieldSelect) {
        fieldSelect.addEventListener("change", function(){
            const params = new URLSearchParams(window.location.search);

            params.set("field_per_page", this.value);

            params.set("field_page", 1);

            window.location.search = params.toString();
        });
    }

    if (caseSelect) {
        caseSelect.addEventListener("change", function(){
            const params = new URLSearchParams(window.location.search);

            params.set("case_per_page", this.value);

            params.set("case_page", 1);

            window.location.search = params.toString();
        });
    }
}); 