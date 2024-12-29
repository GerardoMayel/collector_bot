/* static/js/chat.js */

// Variables globales para el manejo de audio
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

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

// Manejador del formulario para mensajes de texto
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

// Función para inicializar la grabación de audio
async function initializeAudioRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await sendAudioMessage(audioBlob);
            audioChunks = [];
        };
        
        return true;
    } catch (error) {
        console.error('Error al acceder al micrófono:', error);
        return false;
    }
}

// Función para manejar el inicio/fin de la grabación
async function toggleRecording() {
    const voiceButton = document.getElementById('voiceInput');
    const recordingIndicator = document.getElementById('recordingIndicator');
    
    if (!mediaRecorder) {
        const initialized = await initializeAudioRecording();
        if (!initialized) {
            addMessage('No se pudo acceder al micrófono. Por favor, verifica los permisos.');
            return;
        }
    }
    
    if (!isRecording) {
        // Iniciar grabación
        mediaRecorder.start();
        isRecording = true;
        voiceButton.classList.add('recording');
        voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
        recordingIndicator.classList.remove('hidden');
    } else {
        // Detener grabación
        mediaRecorder.stop();
        isRecording = false;
        voiceButton.classList.remove('recording');
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        recordingIndicator.classList.add('hidden');
    }
}

// Función para enviar el audio al servidor
async function sendAudioMessage(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    document.getElementById('typingIndicator').classList.remove('hidden');
    
    try {
        const response = await fetch('/api/audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Si hay transcripción, mostrarla como mensaje del usuario
            if (data.transcription) {
                addMessage(data.transcription, true);
            }
            addMessage(data.response);
        } else {
            addMessage('Lo siento, hubo un error al procesar el audio.');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Error de conexión. Por favor, intenta de nuevo.');
    } finally {
        document.getElementById('typingIndicator').classList.add('hidden');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Manejar submit del formulario
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', handleSubmit);
    }

    // Evento para el botón de voz
    const voiceButton = document.getElementById('voiceInput');
    if (voiceButton) {
        voiceButton.addEventListener('click', toggleRecording);
    }

    // Manejar Enter en el input
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    });

    // Limpiar chat
    document.getElementById('clearChat').addEventListener('click', async function() {
        try {
            const response = await fetch('/api/clear-chat', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error al limpiar el chat');
            }

            // Limpiar el área de mensajes
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="flex items-start space-x-2 bot-message">
                    <div class="flex-shrink-0">
                        <i class="fas fa-robot text-blue-600 text-xl"></i>
                    </div>
                    <div class="flex-1 bg-gray-100 rounded-lg p-3">
                        <p class="text-gray-800">
                            ¡Hola! Soy tu asistente de cobranza virtual. Puedes escribir tu mensaje o usar el micrófono para hablar. 
                            Para comenzar, por favor proporciona tu número de cliente o número de tarjeta.
                        </p>
                    </div>
                </div>
            `;

            // Limpiar el input
            const userInput = document.getElementById('userInput');
            if (userInput) {
                userInput.value = '';
            }

            // Scroll al inicio
            chatMessages.scrollTop = 0;

            // Animación de feedback
            const clearButton = document.getElementById('clearChat');
            clearButton.classList.add('animate-pulse');
            setTimeout(() => {
                clearButton.classList.remove('animate-pulse');
            }, 1000);

        } catch (error) {
            console.error('Error al limpiar el chat:', error);
            // Mostrar mensaje de error al usuario
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.insertAdjacentHTML('beforeend', `
                <div class="flex items-start space-x-2 bot-message">
                    <div class="flex-shrink-0">
                        <i class="fas fa-exclamation-circle text-red-500 text-xl"></i>
                    </div>
                    <div class="flex-1 bg-red-50 rounded-lg p-3">
                        <p class="text-red-600">
                            Hubo un error al limpiar el chat. Por favor, intenta de nuevo.
                        </p>
                    </div>
                </div>
            `);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    });
});

