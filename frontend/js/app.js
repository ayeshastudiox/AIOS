document.addEventListener('DOMContentLoaded', () => {
    let revenueChart = null;
    let categoryChart = null;
    let paymentChart = null;
    let currentData = null;

    // Inject Custom Dark Theme Scrollbar Styles Dynamically
    const customScrollbarStyle = document.createElement('style');
    customScrollbarStyle.innerHTML = `
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0b0f19;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
    `;
    document.head.appendChild(customScrollbarStyle);

    // View Titles Configuration
    const viewMeta = {
        dashboardView: { title: 'Executive Command Dashboard', subtitle: 'Real-Time Business Intelligence & Algorithmic Strategy' },
        terminalView: { title: 'Data Ingestion Terminal', subtitle: 'Upload and manage operational payload batches' },
        analyticsView: { title: 'Analytics Engine', subtitle: 'Detailed breakdowns and multi-variable operations' },
        insightsView: { title: 'AI Strategic Insights', subtitle: 'Groq LLM-synthesized recommendations and insights' },
        meetingSummaryView: { title: 'Meeting Summaries', subtitle: 'Groq AI-powered meeting decisions, actions, and deadlines' },
        reportsView: { title: 'Reports & Export', subtitle: 'Download validated metrics and aggregated summaries' }
    };

    // Navigation View Switcher
    const navItems = document.querySelectorAll('.nav-item');
    const viewPanels = document.querySelectorAll('.view-panel');
    const pageTitle = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetViewId = item.getAttribute('data-view');
            if (!targetViewId) return;

            navItems.forEach(nav => nav.classList.remove('active'));
            viewPanels.forEach(panel => panel.classList.remove('active'));

            item.classList.add('active');
            const targetPanel = document.getElementById(targetViewId);
            if (targetPanel) targetPanel.classList.add('active');

            if (viewMeta[targetViewId]) {
                pageTitle.textContent = viewMeta[targetViewId].title;
                pageSubtitle.textContent = viewMeta[targetViewId].subtitle;
            }
        });
    });

    // Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('csvFileInput');
    const selectedFileName = document.getElementById('selectedFileName');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const generateAiBtn = document.getElementById('generateAiBtn');
    const clearUploadsBtn = document.getElementById('clearUploadsBtn');
    const downloadReportBtn = document.getElementById('downloadReportBtn');
    const quickExportBtn = document.getElementById('quickExportBtn');

    const kpiRevenue = document.getElementById('kpiRevenue');
    const kpiUnits = document.getElementById('kpiUnits');
    const kpiTransactions = document.getElementById('kpiTransactions');
    const kpiAOV = document.getElementById('kpiAOV');

    const tableTopProduct = document.getElementById('tableTopProduct');
    const tableBottomProduct = document.getElementById('tableBottomProduct');
    const tableIngestStatus = document.getElementById('tableIngestStatus');
    const tableStatusPill = document.getElementById('tableStatusPill');
    const aiOutput = document.getElementById('aiOutput');
    const insightsFullConsole = document.getElementById('insightsFullConsole');

    // Main Revenue Line Chart Initialization
    function initChart(labels = [], datasetData = []) {
        const canvas = document.getElementById('revenueChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        const tealGradient = ctx.createLinearGradient(0, 0, 0, 250);
        tealGradient.addColorStop(0, 'rgba(6, 182, 212, 0.45)');
        tealGradient.addColorStop(0.5, 'rgba(10, 185, 129, 0.15)');
        tealGradient.addColorStop(1, 'rgba(10, 13, 20, 0.0)');

        const defaultLabels = ['Cycle 1', 'Cycle 2', 'Cycle 3', 'Cycle 4', 'Cycle 5'];
        const defaultData = [12, 19, 14, 25, 22];

        if (revenueChart) {
            revenueChart.destroy();
        }

        revenueChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.length ? labels : defaultLabels,
                datasets: [{
                    label: 'Revenue Dynamics',
                    data: datasetData.length ? datasetData : defaultData,
                    borderColor: '#06b6d4',
                    borderWidth: 3,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#0a0d14',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    fill: true,
                    backgroundColor: tealGradient,
                    tension: 0.45
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.03)', drawBorder: false },
                        ticks: { color: '#64748b', font: { size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.03)', drawBorder: false },
                        ticks: { color: '#64748b', font: { size: 10 } }
                    }
                }
            }
        });
    }

    // Analytics Engine Charts (Category Bar & Payment Method Doughnut)
    function initAnalyticsCharts(categoryData = {}, paymentData = {}) {
        const catCanvas = document.getElementById('categoryChart');
        if (catCanvas) {
            const ctxCat = catCanvas.getContext('2d');
            if (categoryChart) categoryChart.destroy();

            const defaultCatLabels = ['Electronics', 'SaaS Subscriptions', 'Hardware', 'Services'];
            const defaultCatValues = [4500, 3200, 2100, 1800];

            categoryChart = new Chart(ctxCat, {
                type: 'bar',
                data: {
                    labels: Object.keys(categoryData).length ? Object.keys(categoryData) : defaultCatLabels,
                    datasets: [{
                        label: 'Revenue ($)',
                        data: Object.values(categoryData).length ? Object.values(categoryData) : defaultCatValues,
                        backgroundColor: 'rgba(6, 182, 212, 0.4)',
                        borderColor: '#06b6d4',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 10 } } },
                        y: { grid: { color: 'rgba(255, 255, 255, 0.03)' }, ticks: { color: '#64748b', font: { size: 10 } } }
                    }
                }
            });
        }

        const payCanvas = document.getElementById('paymentChart');
        if (payCanvas) {
            const ctxPay = payCanvas.getContext('2d');
            if (paymentChart) paymentChart.destroy();

            const defaultPayLabels = ['Credit Card', 'Stripe / Online', 'Bank Transfer'];
            const defaultPayValues = [55, 30, 15];

            paymentChart = new Chart(ctxPay, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(paymentData).length ? Object.keys(paymentData) : defaultPayLabels,
                    datasets: [{
                        data: Object.values(paymentData).length ? Object.values(paymentData) : defaultPayValues,
                        backgroundColor: ['#06b6d4', '#10b981', '#f43f5e'],
                        borderColor: '#0a0d14',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#f1f5f9', font: { size: 11 }, padding: 14 }
                        }
                    }
                }
            });
        }
    }

    initChart();
    initAnalyticsCharts();

    // Drag and Drop Logic
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.remove('drag-over');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                selectedFileName.textContent = `Selected: ${files[0].name}`;
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                selectedFileName.textContent = `Selected: ${fileInput.files[0].name}`;
            }
        });
    }

    // Data Ingestion Execution Request
    if (uploadBtn) {
        uploadBtn.addEventListener('click', async () => {
            if (!fileInput.files.length) {
                showStatus('Please select or drop a CSV file first.', '#f59e0b');
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            showStatus('Processing payload execution...', '#06b6d4');

            try {
                const response = await fetch('/upload', { method: 'POST', body: formData });
                if (!response.ok) throw new Error('Ingestion failed');

                const data = await response.json();
                currentData = data;

                kpiRevenue.textContent = `$${(data.total_revenue || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
                kpiUnits.textContent = (data.total_units || 0).toLocaleString();
                kpiTransactions.textContent = (data.total_transactions || 0).toLocaleString();
                
                const aov = data.total_transactions ? (data.total_revenue / data.total_transactions) : 0;
                kpiAOV.textContent = `$${aov.toFixed(2)}`;

                tableTopProduct.textContent = data.top_product || 'N/A';
                tableBottomProduct.textContent = data.bottom_product || 'N/A';
                tableIngestStatus.textContent = 'Active Dataset Loaded';
                tableStatusPill.textContent = 'VERIFIED';
                tableStatusPill.className = 'status-pill status-active';

                if (data.chart_labels && data.chart_values) {
                    initChart(data.chart_labels, data.chart_values);
                }

                initAnalyticsCharts(data.category_breakdown || {}, data.payment_breakdown || {});

                generateAiBtn.disabled = false;
                showStatus('Data successfully ingested & verified.', '#10b981');

            } catch (err) {
                showStatus(`Error: ${err.message}`, '#f43f5e');
            }
        });
    }

    // Groq LLM Strategy Synthesis Execution Request with Clean Formatting Parser
    if (generateAiBtn) {
        generateAiBtn.addEventListener('click', async () => {
            if (!currentData) return;

            const loadingHTML = `<div class="ai-placeholder"><i class="fa-solid fa-spinner fa-spin placeholder-icon"></i><p>Synthesizing insights...</p></div>`;
            aiOutput.innerHTML = loadingHTML;
            if (insightsFullConsole) insightsFullConsole.innerHTML = loadingHTML;

            try {
                const response = await fetch('/generate-insights', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentData)
                });

                if (!response.ok) throw new Error('AI synthesis failed');

                const result = await response.json();
                const rawText = result.insights || '';

                // Clean and structure bullet points nicely into separate spaced blocks
                const formattedHtml = rawText
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line.length > 0)
                    .map(line => {
                        let cleanLine = line.replace(/^([-*]|\d+\.)\s*/, '');
                        cleanLine = cleanLine.replace(/\*\*(.*?)\*\*/g, '<strong style="color:var(--accent-cyan);">$1</strong>');
                        return `<div style="margin-bottom: 14px; line-height: 1.6; padding-left: 4px;">• ${cleanLine}</div>`;
                    })
                    .join('');

                const finalOutput = `<div style="color: var(--text-primary); font-size: 13px;">${formattedHtml}</div>`;
                aiOutput.innerHTML = finalOutput;
                if (insightsFullConsole) insightsFullConsole.innerHTML = finalOutput;

            } catch (err) {
                const errorMsg = `<span style="color: var(--accent-pink);">AI Error: ${err.message}</span>`;
                aiOutput.innerHTML = errorMsg;
                if (insightsFullConsole) insightsFullConsole.innerHTML = errorMsg;
            }
        });
    }
  // Meeting Summaries
const meetingTranscript = document.getElementById('meetingTranscript');
const generateMeetingSummaryBtn = document.getElementById('generateMeetingSummaryBtn');
const meetingSummaryOutput = document.getElementById('meetingSummaryOutput');

if (generateMeetingSummaryBtn) {
    generateMeetingSummaryBtn.addEventListener('click', async () => {
        const transcript = meetingTranscript.value.trim();

        if (!transcript) {
            meetingSummaryOutput.innerHTML = `
                <div style="color: var(--accent-pink); padding: 16px;">
                    Please enter a meeting transcript.
                </div>
            `;
            return;
        }

        meetingSummaryOutput.innerHTML = `
            <div class="ai-placeholder">
                <i class="fa-solid fa-spinner fa-spin placeholder-icon"></i>
                <p>Generating meeting summary...</p>
            </div>
        `;

        generateMeetingSummaryBtn.disabled = true;

        try {
            const response = await fetch('http://127.0.0.1:8000/api/meeting/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    transcript: transcript
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.detail || 'Meeting summary generation failed.'
                );
            }

            const summaryText = result.summary || '';

            const formattedSummary = summaryText
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/^\s*-\s+(.*)$/gm, '<div style="margin-left: 16px; margin-bottom: 6px;">• $1</div>')
                .replace(/\n/g, '<br>');

            meetingSummaryOutput.innerHTML = `
                <div style="
                    color: var(--text-primary);
                    font-size: 13px;
                    line-height: 1.7;
                    padding: 16px;
                ">${formattedSummary}</div>
            `;

        } catch (error) {
            meetingSummaryOutput.innerHTML = `
                <div style="color: var(--accent-pink); padding: 16px;">
                    AI Error: ${error.message}
                </div>
            `;
        } finally {
            generateMeetingSummaryBtn.disabled = false;
        }
    });
}
        // AI Email Writer
const emailRecipient = document.getElementById('emailRecipient');
const emailScenario = document.getElementById('emailScenario');
const emailTone = document.getElementById('emailTone');
const generateEmailBtn = document.getElementById('generateEmailBtn');
const emailOutput = document.getElementById('emailOutput');

if (generateEmailBtn) {
    generateEmailBtn.addEventListener('click', async () => {
        const recipient = emailRecipient.value.trim();
        const scenario = emailScenario.value.trim();
        const tone = emailTone.value;

        if (!recipient || !scenario) {
            emailOutput.innerHTML = `
                <div style="color: var(--accent-pink); padding: 16px;">
                    Please enter both the recipient and email scenario.
                </div>
            `;
            return;
        }

        emailOutput.innerHTML = `
            <div class="ai-placeholder">
                <i class="fa-solid fa-spinner fa-spin placeholder-icon"></i>
                <p>Generating your business email...</p>
            </div>
        `;

        generateEmailBtn.disabled = true;

        try {
            const response = await fetch('http://127.0.0.1:8000/api/email/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipient: recipient,
                    scenario: scenario,
                    tone: tone
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Email generation failed.');
            }

            const emailText = result.email || '';

            emailOutput.innerHTML = `
                <div style="
                    color: var(--text-primary);
                    font-size: 13px;
                    line-height: 1.7;
                    white-space: pre-wrap;
                    padding: 16px;
                ">${emailText}</div>
            `;

        } catch (error) {
            emailOutput.innerHTML = `
                <div style="color: var(--accent-pink); padding: 16px;">
                    AI Error: ${error.message}
                </div>
            `;
        } finally {
            generateEmailBtn.disabled = false;
        }
    });
}
    // Terminal Clear Logic
    if (clearUploadsBtn) {
        clearUploadsBtn.addEventListener('click', () => {
            fileInput.value = '';
            currentData = null;
            selectedFileName.textContent = 'No file target selected';
            
            kpiRevenue.textContent = '$0.00';
            kpiUnits.textContent = '0';
            kpiTransactions.textContent = '0';
            kpiAOV.textContent = '$0.00';

            tableTopProduct.textContent = '—';
            tableBottomProduct.textContent = '—';
            tableIngestStatus.textContent = 'Awaiting File...';
            tableStatusPill.textContent = 'IDLE';
            tableStatusPill.className = 'status-pill status-neutral';

            generateAiBtn.disabled = true;
            initChart();
            initAnalyticsCharts();
            showStatus('Terminal cleared.', '#64748b');
        });
    }

    // CSV Metric Export Handler
    function exportMetricsCSV() {
        if (!currentData) {
            showStatus('No active dataset to export. Ingest a file first.', '#f59e0b');
            alert('No data available to export. Please upload a CSV file first.');
            return;
        }

        const aov = currentData.total_transactions ? (currentData.total_revenue / currentData.total_transactions) : 0;

        const csvRows = [
            ['Metric', 'Value'],
            ['Total Revenue ($)', currentData.total_revenue || 0],
            ['Total Units Sold', currentData.total_units || 0],
            ['Total Transactions', currentData.total_transactions || 0],
            ['Average Order Value ($)', aov.toFixed(2)],
            ['Top Performing Product', `"${currentData.top_product || 'N/A'}"`],
            ['Lowest Volume Product', `"${currentData.bottom_product || 'N/A'}"`]
        ];

        const csvContent = 'data:text/csv;charset=utf-8,' + csvRows.map(e => e.join(',')).join('\n');
        const encodedUri = encodeURI(csvContent);
        
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `executive_report_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        
        link.click();
        document.body.removeChild(link);
    }

    if (downloadReportBtn) {
        downloadReportBtn.addEventListener('click', exportMetricsCSV);
    }

    if (quickExportBtn) {
        quickExportBtn.addEventListener('click', exportMetricsCSV);
    }

                function showStatus(msg, color) {
        if (uploadStatus) {
            uploadStatus.textContent = msg;
            uploadStatus.style.color = color;
        }
    }

});