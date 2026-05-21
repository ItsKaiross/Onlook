// Open print modal and load officers
function openFieldReportPrintModal() {
    const modal = document.getElementById('fieldReportPrintModal');
    modal.classList.add('active');
    loadFieldReportOfficers();
}

// Close print modal
function closeFieldReportPrintModal() {
    const modal = document.getElementById('fieldReportPrintModal');
    modal.classList.remove('active');
    document.getElementById('fieldPreparedBy').value = '';
    document.getElementById('fieldApprovedBy').value = '';
}

// Load all police officers
function loadFieldReportOfficers() {
    fetch('/police-field-report/get-officers')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const preparedBySelect = document.getElementById('fieldPreparedBy');
                const approvedBySelect = document.getElementById('fieldApprovedBy');
                
                preparedBySelect.innerHTML = '<option value="">Select Officer</option>';
                approvedBySelect.innerHTML = '<option value="">Select Officer</option>';
                
                data.officers.forEach(officer => {
                    const option1 = document.createElement('option');
                    option1.value = officer.name;
                    option1.textContent = officer.name;
                    preparedBySelect.appendChild(option1);
                    
                    const option2 = document.createElement('option');
                    option2.value = officer.name;
                    option2.textContent = officer.name;
                    approvedBySelect.appendChild(option2);
                });
            }
        })
        .catch(err => {
            console.error('Error loading officers:', err);
            alert('Failed to load officers list');
        });
}

// Confirm and print
function confirmFieldReportPrint() {
    const preparedBy = document.getElementById('fieldPreparedBy').value;
    const approvedBy = document.getElementById('fieldApprovedBy').value;
    
    if (!preparedBy || !approvedBy) {
        alert('Please select both Prepared By and Approved By');
        return;
    }
    
    closeFieldReportPrintModal();
    printFieldReport(preparedBy, approvedBy);
}

function printFieldReport(preparedBy, approvedBy) {
    const btn = document.querySelector(".print_table_btn");
    btn.textContent = "Loading...";
    btn.disabled = true;

    const params = new URLSearchParams(window.location.search);
    const status = params.get('status') || '';
    const dateFrom = params.get('date_from') || '';
    const dateTo = params.get('date_to') || '';
    const ageRange = params.get('age_range') || '';

    const queryParams = new URLSearchParams();
    if (status) queryParams.set('status', status);
    if (dateFrom) queryParams.set('date_from', dateFrom);
    if (dateTo) queryParams.set('date_to', dateTo);
    if (ageRange) queryParams.set('age_range', ageRange);

    fetch(`/police-field-report/filtered?${queryParams.toString()}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) throw new Error(data.error);

            const rows = data.reports.map(r => `
                <tr>
                    <td>${r.case_id}</td>
                    <td>${r.full_name || ''}</td>
                    <td>${r.age || ''}</td>
                    <td>${r.date_last_seen || ''}</td>
                    <td>${r.approval_status || ''}</td>
                </tr>
            `).join('');

            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Field Report</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .pnp-header {
                            text-align: center;
                            margin-bottom: 30px;
                            border-bottom: 3px solid #1A1B41;
                            padding-bottom: 15px;
                        }
                        .pnp-header h1 {
                            margin: 0;
                            font-size: 20px;
                            font-weight: bold;
                            color: #1A1B41;
                        }
                        .pnp-header h2 {
                            margin: 5px 0 0 0;
                            font-size: 16px;
                            font-weight: normal;
                            color: #333;
                        }
                        .pnp-header p {
                            margin: 3px 0 0 0;
                            font-size: 13px;
                            color: #666;
                        }
                        h2 { margin-bottom: 4px; }
                        p { margin-bottom: 16px; color: #666; font-size: 13px; }
                        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                        th, td { border: 1px solid #ccc; padding: 10px; text-align: left; font-size: 13px; }
                        th { background-color: #f4f4f4; font-weight: 600; }
                        tr:nth-child(even) { background-color: #f9f9f9; }
                        .signature-section {
                            display: flex;
                            justify-content: space-between;
                            margin-top: 40px;
                            padding: 0 50px;
                        }
                        .signature-box {
                            text-align: center;
                            min-width: 200px;
                        }
                        .signature-line {
                            border-top: 2px solid #000;
                            margin-top: 50px;
                            padding-top: 8px;
                            font-weight: bold;
                        }
                        .signature-label {
                            font-size: 9pt;
                            color: #666;
                            margin-top: 4px;
                        }
                        @media print { body { padding: 0; } }
                    </style>
                </head>
                <body>
                    <div class="pnp-header">
                        <h1>PHILIPPINE NATIONAL POLICE</h1>
                        <h2>Police Provincial Office of Laguna</h2>
                        <p>Missing Persons Unit - Field Report</p>
                    </div>
                    <h2>Field Report</h2>
                    <p>Printed on: ${new Date().toLocaleDateString()} · Total records: ${data.reports.length}</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Case #</th>
                                <th>Name</th>
                                <th>Age</th>
                                <th>Last Seen</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                    <div class="signature-section">
                        <div class="signature-box">
                            <div class="signature-line">${preparedBy}</div>
                            <div class="signature-label">Prepared By</div>
                        </div>
                        <div class="signature-box">
                            <div class="signature-line">${approvedBy}</div>
                            <div class="signature-label">Approved By</div>
                        </div>
                    </div>
                </body>
                </html>
            `);

            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
            printWindow.close();
        })
        .catch(err => {
            console.error("Print error:", err);
            alert("Error loading data for print: " + err.message);
        })
        .finally(() => {
            btn.textContent = "Print Table";
            btn.disabled = false;
        });
}