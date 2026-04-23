document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('uploadStatus');
    
    if (fileInput.files.length === 0) return;
    
    const formData = new FormData();
    formData.append('payload_file', fileInput.files[0]);
    
    statusDiv.innerHTML = 'Uploading dataset...';
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            statusDiv.innerHTML = `<span style="color: green;">Upload successful! Task ID: ${data.id}</span>`;
            fileInput.value = '';
            loadTasks();
        } else {
            const errorData = await response.json();
            statusDiv.innerHTML = `<span style="color: red;">Failed to upload: ${errorData.detail}</span>`;
        }
    } catch (error) {
        console.error("Upload failed:", error);
        statusDiv.innerHTML = `<span style="color: red;">Network error: ${error.message}</span>`;
    }
});

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        
        const tableBody = document.querySelector('#taskTable tbody');
        tableBody.innerHTML = '';
        
        tasks.forEach(task => {
            const tableRow = document.createElement('tr');
            tableRow.innerHTML = `
                <td>${task.id.substring(0, 8)}...</td>
                <td>${task.dataset_id || 'N/A'}</td>
                <td class="status-${task.status}">${task.status}</td>
                <td>${new Date(task.created_at).toLocaleString()}</td>
                <td><button onclick="showTask('${task.id}')">View Details</button></td>
            `;
            tableBody.appendChild(tableRow);
        });
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
}

async function showTask(taskId) {
    const detailsContainer = document.getElementById('taskDetails');
    const contentContainer = document.getElementById('taskContent');
    
    detailsContainer.style.display = 'block';
    contentContainer.innerHTML = 'Loading task details...';
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        const task = await response.json();
        
        let htmlContent = `
            <p><strong>Task ID:</strong> ${task.id}</p>
            <p><strong>Dataset ID:</strong> ${task.dataset_id || 'N/A'}</p>
            <p><strong>Current Status:</strong> <span class="status-${task.status}">${task.status}</span></p>
            <p><strong>Created At:</strong> ${new Date(task.created_at).toLocaleString()}</p>
        `;
        
        if (task.status === 'Completed') {
            htmlContent += `
                <hr/>
                <h3>Results</h3>
                <p><strong>Record Count:</strong> ${task.record_count}</p>
                <p><strong>Average Value:</strong> ${task.average_value}</p>
                <p><strong>Invalid Records:</strong> ${task.invalid_records}</p>
                <h4>Category Summary:</h4>
                <pre>${JSON.stringify(task.category_summary, null, 2)}</pre>
            `;
        } else if (task.status === 'Failed') {
            htmlContent += `<p><strong>Error Details:</strong> <span style="color: red;">${task.error_message}</span></p>`;
        } else {
            htmlContent += `<p><em>Task is currently processing. Please check back in a few seconds...</em></p>`;
        }
        
        contentContainer.innerHTML = htmlContent;
    } catch (error) {
        console.error("Error fetching task details:", error);
        contentContainer.innerHTML = `<span style="color: red;">Error: ${error.message}</span>`;
    }
}

// Initial load and periodic polling
loadTasks();
setInterval(loadTasks, 5000);
