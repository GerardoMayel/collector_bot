/* static/js/chat.js */
// Función para agregar mensajes al chat
function addMessage(text, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start space-x-2 ${isUser ? 'justify-end' : ''}`;

    const content = `
        ${!isUser ? '<div class="flex-shrink-0"><i class="fas fa-robot text-blue-600 text-xl"></i></div>' : ''}
        <div class="${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'} rounded-lg p-3 max-w-[70%]">
            <p>${text}</p>
        </div>
    `;

    messageDiv.innerHTML = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Manejador del formulario
async function handleSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;

    // Deshabilitar input mientras se procesa
    input.disabled = true;
    document.querySelector('#chatForm button').disabled = true;

    // Mostrar el mensaje del usuario
    addMessage(message, true);
    input.value = '';

    // Mostrar indicador de escritura
    document.getElementById('typingIndicator').classList.remove('hidden');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        
        if (response.ok) {
            addMessage(data.response);
        } else {
            addMessage('Lo siento, hubo un error al procesar tu mensaje.');
        }
    } catch (error) {
        addMessage('Error de conexión. Por favor, intenta de nuevo.');
        console.error('Error:', error);
    } finally {
        // Habilitar input después del proceso
        input.disabled = false;
        document.querySelector('#chatForm button').disabled = false;
        document.getElementById('typingIndicator').classList.add('hidden');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Evento para el botón de voz
    const voiceButton = document.getElementById('voiceInput');
    if (voiceButton) {
        voiceButton.addEventListener('click', () => {
            // Implementar funcionalidad de voz aquí
            alert('Funcionalidad de voz en desarrollo');
        });
    }

    // Manejar Enter en el input
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    });
});