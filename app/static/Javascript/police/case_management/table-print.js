// Open print modal and load officers
function openCasePrintModal() {
    const modal = document.getElementById('casePrintModal');
    modal.classList.add('active');
    loadCaseOfficers();
}

// Close print modal
function closeCasePrintModal() {
    const modal = document.getElementById('casePrintModal');
    modal.classList.remove('active');
    document.getElementById('casePreparedBy').value = '';
    document.getElementById('caseApprovedBy').value = '';
}

// Load all police officers
function loadCaseOfficers() {
    fetch('/police-case-report/get-officers')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const preparedBySelect = document.getElementById('casePreparedBy');
                const approvedBySelect = document.getElementById('caseApprovedBy');
                
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
function confirmCasePrint() {
    const preparedBy = document.getElementById('casePreparedBy').value;
    const approvedBy = document.getElementById('caseApprovedBy').value;
    
    if (!preparedBy || !approvedBy) {
        alert('Please select both Prepared By and Approved By');
        return;
    }
    
    closeCasePrintModal();
    printCaseManagement(preparedBy, approvedBy);
}

function printCaseManagement(preparedBy, approvedBy) {
    const btn = document.querySelector(".print-table-btn");
    btn.textContent = "Loading...";
    btn.disabled = true;

    const params = new URLSearchParams(window.location.search);
    const status = params.get('status') || '';
    const fromDate = params.get('from_date') || '';
    const toDate = params.get('to_date') || '';
    const showArchived = params.get('show_archived') || '';

    const queryParams = new URLSearchParams();
    if (status) queryParams.set('status', status);
    if (fromDate) queryParams.set('from_date', fromDate);
    if (toDate) queryParams.set('to_date', toDate);
    if (showArchived) queryParams.set('show_archived', showArchived);

    fetch(`/police-case-report/filtered?${queryParams.toString()}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) throw new Error(data.error);

            const rows = data.reports.map(r => `
                <tr>
                    <td>${r.case_id}</td>
                    <td>${r.full_name || ''}</td>
                    <td>${r.case_status || ''}</td>
                    <td>${r.priority || ''}</td>
                    <td>${r.assigned_officer || ''}</td>
                </tr>
            `).join('');

            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Cases</title>
                    <style>
                        @page { size: A4 landscape; margin: 15mm; }
                        
                        * { box-sizing: border-box; margin: 0; padding: 0; }
                        
                        body { 
                            font-family: "Times New Roman", serif; 
                            padding: 20px; 
                            font-size: 12pt;
                            color: #000;
                            background: white;
                        }

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

                        .print-header {
                            display: flex;
                            align-items: center;
                            gap: 16px;
                            margin-bottom: 16px;
                            padding-bottom: 12px;
                            border-bottom: 3px solid #1A1B41;
                        }

                        .print-header .logo-circle {
                            width: 60px;
                            height: 60px;
                            background: #1A1B41;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-size: 20px;
                            font-weight: bold;
                            flex-shrink: 0;
                        }

                        .print-header .header-text h1 {
                            font-size: 18px;
                            font-weight: bold;
                            color: #1A1B41;
                        }

                        .print-header .header-text p {
                            font-size: 11px;
                            color: #555;
                            margin-top: 2px;
                        }

                        .print-header .header-meta {
                            margin-left: auto;
                            text-align: right;
                            font-size: 11px;
                            color: #555;
                        }

                        table { 
                            border-collapse: collapse; 
                            width: 100%; 
                            font-size: 9pt;
                            margin-top: 20px;
                        }

                        thead tr {
                            background: #1A1B41;
                            color: white;
                        }

                        th { 
                            padding: 8px 6px;
                            text-align: center;
                            font-weight: bold;
                            font-size: 9pt;
                            border: 1px solid #1A1B41;
                        }

                        td { 
                            border: 1px solid #ccc;
                            padding: 6px;
                            text-align: center;
                            vertical-align: middle;
                        }

                        tr:nth-child(even) td { background: #f5f5f5; }
                        tr:nth-child(odd) td  { background: white; }

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

                        @media print { 
                            body { padding: 0; }
                        }
                    </style>
                </head>
                <body>
                    <div class="pnp-header">
                        <h1>PHILIPPINE NATIONAL POLICE</h1>
                        <h2>Police Provincial Office of Laguna</h2>
                        <p>Missing Persons Unit - Case Management</p>
                    </div>
                    <h2>Cases</h2>
                    <p>Printed on: ${new Date().toLocaleDateString()} · Total records: ${data.reports.length}</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Case #</th>
                                <th>Name</th>
                                <th>Case Status</th>
                                <th>Priority</th>
                                <th>Assigned to</th>
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
            printWindow.onload = function() {
                printWindow.print();
                printWindow.onafterprint = function() { printWindow.close(); };
            };
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