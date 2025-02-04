import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

app = FastAPI()

# Додаємо підтримку CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Додаємо шаблони та статику
templates = Jinja2Templates(directory="./app/templates")
app.mount("/static", StaticFiles(directory="./app/static"), name="static")


# Менеджер WebSocket-з'єднань
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # {client_id: connection}
        self.usernames: dict[str, str] = {}  # {client_id: username}

    async def connect(self, websocket: WebSocket, username: str):
        if not username.strip():  # Перевіряємо, чи є ім'я
            await websocket.close()
            return None  # Не підключаємо без імені

        client_id = str(uuid.uuid4())  # Генеруємо унікальний ID
        self.active_connections[client_id] = websocket
        self.usernames[client_id] = username
        await self.broadcast(f"📩 🟢 {username} приєднався до чату.", sender_id=None)
        return client_id

    async def disconnect(self, client_id: str):
        if client_id and client_id in self.active_connections:
            username = self.usernames.pop(client_id, None)  # Видаляємо користувача
            del self.active_connections[client_id]
            if username:
                await self.broadcast(f"📩 🔴 {username} покинув чат.", sender_id=None)

    async def broadcast(self, message: str, sender_id: str = None):
        sender_name = self.usernames.get(sender_id, "")
        for client_id, connection in self.active_connections.items():
            if sender_id is None:
                # Для системних повідомлень (підключення/відключення)
                formatted_message = message
            elif client_id == sender_id:
                # Якщо це той самий користувач — відображаємо "Ви:"
                formatted_message = f"Ви: {message}"
            else:
                # Для інших показуємо його нікнейм
                formatted_message = f"📩 {sender_name}: {message}"

            await connection.send_json({"message": formatted_message})


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # ✅ Приймаємо WebSocket тільки тут

    try:
        data = await websocket.receive_json()  # Отримуємо ім'я користувача
        username = data.get("username", "").strip()
        client_id = await manager.connect(websocket, username)

        if not client_id:  # Якщо клієнт не підключився (не вказав ім'я)
            return

        while True:
            message = await websocket.receive_text()
            if client_id not in manager.active_connections:  # Якщо юзер вийшов — не даємо писати
                break
            await manager.broadcast(message, sender_id=client_id)

    except WebSocketDisconnect:
        await manager.disconnect(client_id)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
