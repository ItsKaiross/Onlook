// Open print modal and load officers
function openPrintModal() {
    const modal = document.getElementById('printModal');
    modal.classList.add('active');
    loadOfficers();
}

// Close print modal
function closePrintModal() {
    const modal = document.getElementById('printModal');
    modal.classList.remove('active');
    document.getElementById('preparedBy').value = '';
    document.getElementById('approvedBy').value = '';
}

// Load all police officers including police admin
function loadOfficers() {
    console.log('Loading officers...');
    fetch('/admin-reports/get-officers')
        .then(res => {
            console.log('Response status:', res.status);
            return res.json();
        })
        .then(data => {
            console.log('Officers data:', data);
            if (data.success) {
                const preparedBySelect = document.getElementById('preparedBy');
                const approvedBySelect = document.getElementById('approvedBy');
                
                console.log('Dropdowns found:', preparedBySelect, approvedBySelect);
                
                // Clear existing options except the first one
                preparedBySelect.innerHTML = '<option value="">Select Officer</option>';
                approvedBySelect.innerHTML = '<option value="">Select Officer</option>';
                
                console.log('Number of officers:', data.officers.length);
                
                // Populate both dropdowns
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
                
                console.log('Officers loaded successfully');
            } else {
                console.error('API returned success=false:', data);
                alert('Failed to load officers: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(err => {
            console.error('Error loading officers:', err);
            alert('Failed to load officers list: ' + err.message);
        });
}

// Confirm and print
function confirmPrint() {
    const preparedBy = document.getElementById('preparedBy').value;
    const approvedBy = document.getElementById('approvedBy').value;
    
    if (!preparedBy || !approvedBy) {
        alert('Please select both Prepared By and Approved By');
        return;
    }
    
    closePrintModal();
    printAdminReports(preparedBy, approvedBy);
}

function printAdminReports(preparedBy, approvedBy) {
    const btn = document.querySelector("#printBtn");
    btn.textContent = "Loading...";
    btn.disabled = true;

    // Get current filter values
    const month = document.querySelector('select[name="month"]').value;
    const year = document.querySelector('input[name="year"]').value;
    const precinct = document.querySelector('select[name="precinct"]').value;

    // Build query parameters
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    if (precinct) params.append('precinct', precinct);

    fetch(`/admin-reports/print?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) throw new Error(data.error);

            const rows = data.reports.map((r, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td>${r.full_name || ''}</td>
                    <td>${r.age || ''}</td>
                    <td>${r.gender || ''}</td>
                    <td>${r.address || ''}</td>
                    <td>${r.date_missing || ''}</td>
                    <td>${r.date_reported || ''}</td>
                    <td>${r.precinct || ''}</td>
                    <td>${r.reason || '-'}</td>
                    <td>${r.found_dead ? 'YES' : 'NO'}</td>
                    <td>${r.found_alive ? 'YES' : 'NO'}</td>
                    <td>${r.cause_of_death || '-'}</td>
                    <td>${r.still_missing ? 'YES' : 'NO'}</td>
                    <td>${r.docket_number || '-'}</td>
                    <td>${r.investigator_name || '-'}</td>
                </tr>
            `).join('');

            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Admin Reports - Missing Minors</title>
                    <style>
                        @page { size: A4 landscape; margin: 10mm; }
                        
                        * { box-sizing: border-box; margin: 0; padding: 0; }
                        
                        body { 
                            font-family: "Times New Roman", serif; 
                            padding: 15px; 
                            font-size: 10pt;
                            color: #000;
                            background: white;
                        }

                        .pnp-header {
                            text-align: center;
                            margin-bottom: 25px;
                            border-bottom: 3px solid #1A1B41;
                            padding-bottom: 15px;
                        }
                        .pnp-header h1 {
                            margin: 0;
                            font-size: 18px;
                            font-weight: bold;
                            color: #1A1B41;
                        }
                        .pnp-header h2 {
                            margin: 5px 0 0 0;
                            font-size: 14px;
                            font-weight: normal;
                            color: #333;
                        }
                        .pnp-header p {
                            margin: 3px 0 0 0;
                            font-size: 11px;
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
                            width: 50px;
                            height: 50px;
                            background: #1A1B41;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: white;
                            font-size: 16px;
                            font-weight: bold;
                            flex-shrink: 0;
                        }

                        .print-header .header-text h1 {
                            font-size: 16px;
                            font-weight: bold;
                            color: #1A1B41;
                        }

                        .print-header .header-text p {
                            font-size: 10px;
                            color: #555;
                            margin-top: 2px;
                        }

                        .print-header .header-meta {
                            margin-left: auto;
                            text-align: right;
                            font-size: 10px;
                            color: #555;
                        }

                        table { 
                            border-collapse: collapse; 
                            width: 100%; 
                            font-size: 8pt;
                            margin-top: 10px;
                        }

                        thead tr {
                            background: #1A1B41;
                            color: white;
                        }

                        th { 
                            padding: 6px 4px;
                            text-align: center;
                            font-weight: bold;
                            font-size: 7pt;
                            border: 1px solid #1A1B41;
                            vertical-align: middle;
                        }

                        td { 
                            border: 1px solid #ccc;
                            padding: 4px 3px;
                            text-align: center;
                            vertical-align: middle;
                            font-size: 7pt;
                        }

                        tr:nth-child(even) td { background: #f5f5f5; }
                        tr:nth-child(odd) td  { background: white; }

                        .print-footer {
                            margin-top: 20px;
                            padding-top: 12px;
                            border-top: 1px solid #ccc;
                            font-size: 9pt;
                            color: #333;
                        }

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
                        <p>Missing Minors Administrative Report</p>
                    </div>
                    
                    <div class="print-header">
                        <div class="header-text">
                            <h1>Missing Minors Report</h1>
                            <p>Administrative Report - Police Department</p>
                        </div>
                        <div class="header-meta">
                            <div>Generated: ${new Date().toLocaleDateString()}</div>
                            <div>Total Records: ${data.reports.length}</div>
                        </div>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th rowspan="2">No.</th>
                                <th rowspan="2">Name of Missing Minor</th>
                                <th rowspan="2">Age</th>
                                <th rowspan="2">Sex</th>
                                <th rowspan="2">Address</th>
                                <th rowspan="2">Date Missing</th>
                                <th rowspan="2">Date Reported</th>
                                <th rowspan="2">Police Station</th>
                                <th rowspan="2">Reason</th>
                                <th colspan="2">Found</th>
                                <th rowspan="2">Cause of Death</th>
                                <th rowspan="2">Still Missing</th>
                                <th rowspan="2">Docket No. / Criminal Case</th>
                                <th rowspan="2">Investigator-on-Case</th>
                            </tr>
                            <tr>
                                <th>Dead</th>
                                <th>Alive</th>
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
                    
                    <div class="print-footer">
                        <div style="text-align: center;">OnLook System - Administrative Report</div>
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
            btn.textContent = "Print Report";
            btn.disabled = false;
        });
}