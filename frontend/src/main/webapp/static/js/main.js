// Chat functionality
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');

async function sendMessage() {
    const message = userInput.value;
    if (!message) return;

    // Add user message to chat
    appendMessage('user', message);
    userInput.value = '';

    try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        appendMessage('bot', data.message);

        // If there's a task, update the dashboard
        if (data.task) {
            updateDashboard(data.task);
        }
    } catch (error) {
        console.error('Error:', error);
        appendMessage('bot', 'Sorry, there was an error processing your request.');
    }
}

function appendMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Dashboard functionality
function updateDashboard(task) {
    const dashboard = document.getElementById('dashboard');
    const taskElement = document.createElement('div');
    taskElement.className = 'task-card';
    taskElement.innerHTML = `
        <h3>Task: ${task.name}</h3>
        <p>Status: ${task.status}</p>
        <p>Created: ${new Date(task.createdAt).toLocaleString()}</p>
    `;
    dashboard.appendChild(taskElement);
} 