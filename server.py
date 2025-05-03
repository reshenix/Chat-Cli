
# server.py
import websockets
import asyncio
import logging
import enum

from typing import Optional
from utils import initialize_logging

# Initialize logging
initialize_logging()

class Client:
    def __init__(self, websocket):
        self.websocket = websocket
        self.remote_address = websocket.remote_address

class MessageType(enum.Enum):
    USER = "user"
    SERVER = "server"

class Message:
    def __init__(self, content: str, sender: Optional[Client] = None, type: MessageType = MessageType.USER):
        self.content = content
        self.sender = sender
        self.type = type

    def __str__(self):
        if self.type == MessageType.USER and self.sender:
            return f"{self.sender.remote_address}: {self.content}"
        elif self.type == MessageType.SERVER:
            return f"{self.content}"
        else:
            return f"{self.content}"

clients = set()

async def handler(websocket) -> None:
    client = Client(websocket)
    await connect(client)
    try:
        # Listen for incoming messages
        async for message in websocket:
            await broadcast(message, client)
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"{client.remote_address} disconnected.")
    finally:
        # Remove client from the list of connected clients
        await disconnect(client)

# Broadcast message to all connected clients, except the sender (if sender is provided)
async def broadcast(message: str, sender: Optional[Client] = None, type: MessageType = MessageType.USER) -> None:
    msg = Message(message, sender, type)
    for client in clients:
        # Check if this client is not the sender
        if client != sender:
            try:
                await client.websocket.send(str(msg))
            except websockets.exceptions.ConnectionClosed:
                # Remove client from the list of connected clients
                await disconnect(client)

# Connect client to the server
async def connect(client: Client) -> None:
    clients.add(client)
    logging.info(f"{client.remote_address} connected.")
    await broadcast(f"{client.remote_address} connected.", client, type=MessageType.SERVER)

# Disconnect client from the server
async def disconnect(client: Client) -> None:
    clients.discard(client)
    try:
        await broadcast(f"{client.remote_address} disconnected.", client, type=MessageType.SERVER)
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"{client.remote_address} disconnected.")

# Main function to run the server
async def main() -> None:
    async with websockets.serve(handler, "127.0.0.1", 8888):
        await asyncio.Future()

# Run the server
asyncio.run(main())
