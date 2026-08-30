const API_BASE_URL = "http://127.0.0.1:8000";

let currentUploadedFilename = "";

const fileInput = document.getElementById("csvFileInput");
const selectedFileName = document.getElementById("selectedFileName");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const generateAiBtn = document.getElementById("generateAiBtn");
const aiOutput = document.getElementById("aiOutput");

// Handle File Selection
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        selectedFileName.textContent = fileInput.files[0].name;
    }
});

// 1. Trigger File Upload & Analytics
uploadBtn.addEventListener("click", async () => {
    if (!fileInput.files.length) {
        uploadStatus.style.color = "#ff4d4d";
        uploadStatus.textContent = "Please select a CSV file first.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    uploadStatus.style.color = "#00f0ff";
    uploadStatus.textContent = "Uploading file to backend...";

    try {
        // Post File to /api/upload
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentUploadedFilename = data.filename;
            uploadStatus.style.color = "#00ff88";
            uploadStatus.textContent = "File uploaded successfully! Fetching analytics...";
            
            // Enable AI button and load calculated analytics
            generateAiBtn.disabled = false;
            fetchAnalytics(currentUploadedFilename);
        } else {
            uploadStatus.style.color = "#ff4d4d";
            uploadStatus.textContent = data.detail || "Upload failed.";
        }
    } catch (err) {
        uploadStatus.style.color = "#ff4d4d";
        uploadStatus.textContent = "Error connecting to backend server.";
    }
});

// 2. Fetch Analytics Metrics
async function fetchAnalytics(filename) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/analytics/${filename}`);
        const result = await response.json();

        if (response.ok) {
            const data = result.data;
            document.getElementById("kpiRevenue").textContent = `$${data.total_revenue.toLocaleString()}`;
            document.getElementById("kpiUnits").textContent = data.total_units_sold.toLocaleString();
            document.getElementById("kpiTransactions").textContent = data.total_transactions.toLocaleString();
            document.getElementById("kpiAOV").textContent = `$${data.average_order_value}`;
        }
    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}

// 3. Trigger Groq AI Insights
generateAiBtn.addEventListener("click", async () => {
    if (!currentUploadedFilename) return;

    aiOutput.innerHTML = `<p style="color: #00f0ff;"><i class="fa-solid fa-spinner fa-spin"></i> Groq AI is generating strategic insights...</p>`;

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-insights?filename=${currentUploadedFilename}`, {
            method: "POST"
        });

        const result = await response.json();

        if (response.ok) {
            const insights = result.insights;
            aiOutput.innerHTML = `
                <div style="margin-bottom: 12px;">
                    <strong style="color: #00f0ff;">Key Insights:</strong>
                    <p>${typeof insights.insights === 'object' ? JSON.stringify(insights.insights) : insights.insights}</p>
                </div>
                <div>
    <strong style="color: #00ff88;">Recommendations:</strong>
    <ol style="margin-top: 8px; padding-left: 25px;">
        ${Array.isArray(insights.recommendations)
            ? insights.recommendations.map(rec => `<li style="padding-left: 5px;">${rec}</li>`).join('')
            : `<li style="padding-left: 5px;">${insights.recommendations}</li>`}
    </ol>
</div>
            `;
        } else {
            aiOutput.innerHTML = `<p style="color: #ff4d4d;">Failed to generate AI insights.</p>`;
        }
    } catch (err) {
        aiOutput.innerHTML = `<p style="color: #ff4d4d;">Backend network error.</p>`;
    }
});