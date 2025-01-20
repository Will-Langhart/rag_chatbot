const chatForm = document.getElementById('chat-form');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');

// Function to append a message to the chat
function appendMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
}

// Function to handle backend responses and errors
async function sendMessageToBackend(message) {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: 1, // Replace with a dynamic user ID if needed
                message: message,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            if (data.response) {
                appendMessage(data.response, 'bot');
            } else {
                appendMessage('The chatbot did not provide a response.', 'bot');
                console.error('Unexpected response format:', data);
            }
        } else {
            appendMessage('Error: Unable to connect to the chatbot.', 'bot');
            console.error('Backend returned error:', response.status, response.statusText);
        }
    } catch (error) {
        appendMessage('Error: Something went wrong while communicating with the chatbot.', 'bot');
        console.error('Fetch error:', error);
    }
}

// Event listener for form submission
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = userInput.value.trim();

    if (!message) {
        appendMessage('Please enter a message.', 'bot');
        return;
    }

    // Append user message to chat and clear input
    appendMessage(message, 'user');
    userInput.value = '';

    // Send message to the backend
    sendMessageToBackend(message);
});
