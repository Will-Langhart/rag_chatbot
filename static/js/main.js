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

// Event listener for form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();

    if (!message) return;

    // Append user message to chat
    appendMessage(message, 'user');
    userInput.value = '';

    // Send message to the backend
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
            appendMessage(data.response, 'bot');
        } else {
            appendMessage('Error: Unable to connect to the chatbot.', 'bot');
        }
    } catch (error) {
        appendMessage('Error: Something went wrong.', 'bot');
        console.error('Chat error:', error);
    }
});
