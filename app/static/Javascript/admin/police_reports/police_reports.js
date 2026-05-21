document.addEventListener('DOMContentLoaded', function () {

    const generateBtn = document.getElementById('generateBtn');

    if (generateBtn) {
        generateBtn.addEventListener('click', function () {
            const month = document.querySelector('select[name="month"]').value;
            const year  = document.querySelector('input[name="year"]').value;

            // Disable button while loading
            generateBtn.disabled    = true;
            generateBtn.textContent = 'Generating...';

            fetch(GENERATE_REPORT_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ month: month, year: year })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                console.error('Request failed:', err);
                alert('Something went wrong. Please try again.');
            })
            .finally(() => {
                generateBtn.disabled    = false;
                generateBtn.textContent = 'Generate Report for This Month';
            });
        });
    }

});