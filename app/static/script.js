let socket;

function connectWebSocket() {
    let username = document.getElementById("username").value;
    if (!username) {
        alert("Введіть ваше ім'я!");
        return;
    }

    socket = new WebSocket(`ws://localhost:8000/ws`);

    socket.onopen = () => {
        console.log("Підключено до WebSocket сервера");
        socket.send(JSON.stringify({ username }));  // Відправляємо ім'я відразу після підключення
        addMessage(`🟢 Ви приєдналися як ${username}`, "system-message");
        document.getElementById("connectBtn").disabled = true;
        document.getElementById("disconnectBtn").disabled = false;
    };

    socket.onmessage = (event) => {
        let data = JSON.parse(event.data);
        addMessage(`📩 ${data.message}`, "server-message");
    };

    socket.onclose = () => {
        console.log("З'єднання закрито");
        addMessage("❌ Ви покинули чат", "system-message");
        document.getElementById("connectBtn").disabled = false;
        document.getElementById("disconnectBtn").disabled = true;
    };
}

function sendMessage() {
    let message = document.getElementById("messageInput").value;
    if (message && socket) {
        socket.send(message);
        addMessage(`Ви: ${message}`, "user-message");
        document.getElementById("messageInput").value = "";
    }
}

function disconnectWebSocket() {
    if (socket) {
        socket.close();
    }
}

function addMessage(msg, className) {
    let chatWindow = document.getElementById("chatWindow");
    let messageElement = document.createElement("p");
    messageElement.textContent = msg;
    messageElement.classList.add(className);
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
