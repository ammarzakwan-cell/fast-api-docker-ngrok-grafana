from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Query
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
from collections import deque
import asyncio, json
from typing import Dict

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Constants
VALID_TOKEN = "valid_token"  # Replace with your actual token validation logic
MAX_MESSAGE_LENGTH = 1000  # Maximum allowed message length
MAX_MESSAGES_PER_SECOND = 5  # Rate limit: max messages per second per client
MESSAGE_HISTORY_SIZE = 10  # Number of messages to keep in history

# Thread-safe data structures
connected_clients: Dict[WebSocket, str] = {}
message_history = deque(maxlen=MESSAGE_HISTORY_SIZE)

# Serve HTML page
@app.get("/")
async def get():
    with open("/srv/templates/index.html", "r") as file:
        return HTMLResponse(content=file.read())

async def authenticate_client(websocket: WebSocket) -> bool:
    """
    Authenticate the client using a token sent in the query parameters.
    Returns True if authentication is successful, otherwise False.
    """
    token = websocket.query_params.get("token")
    if not token or not validate_token(token):
        await websocket.send_text("Authentication failed. Invalid or missing token.")
        await websocket.close(code=1008)  # Policy violation
        return False
    return True

def validate_token(token: str) -> bool:
    """
    Validate the token (replace with real validation logic).
    """
    return token == VALID_TOKEN

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, name: str = Query(None)):
    await websocket.accept()

    # Authenticate client before allowing communication
    if not await authenticate_client(websocket):
        return  # Stop execution if authentication fails

    if not name or name.strip() == "":
        name = websocket.headers.get("X-Forwarded-For", websocket.client.host) 
        if not name:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # Add client to connected clients
    connected_clients[websocket] = name

    # Send chat history to the new client
    for sender, message in message_history:
        await websocket.send_text(f"{sender}: {message}")

    # Rate limiting
    message_times = deque(maxlen=MAX_MESSAGES_PER_SECOND)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                name = message_data.get("name", "Unknown")
                message = message_data.get("message", "No message")
            except json.JSONDecodeError:
                name = "Unknown"
                message = data     # Parse incoming JSON

            # Validate message length
            if len(data) > MAX_MESSAGE_LENGTH:
                await websocket.send_text("Message too long")
                continue

            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            message_times.append(current_time)
            if len(message_times) == MAX_MESSAGES_PER_SECOND and (current_time - message_times[0]) < 1:
                await websocket.send_text("Rate limit exceeded")
                continue

            # Store message in history
            message_history.append((name, message))

            # Broadcast message to all clients
            for client, ip in connected_clients.items():
                try:
                    await client.send_text(f"{name}: {message}")
                except Exception as e:
                    # Handle disconnected clients
                    connected_clients.pop(client, None)

    except WebSocketDisconnect:
        connected_clients.pop(websocket, None)
    except Exception as e:
        # Log the error and close the connection
        print(f"Error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)