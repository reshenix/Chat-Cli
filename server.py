
# server.py
import websockets
import asyncio
import logging

# Setting up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Client:
    def __init__(self, websocket):
        self.websocket = websocket
        self.remote_address = websocket.remote_address

clients = set()

async def handler(websocket):
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
async def broadcast(message, sender=None):
    for client in clients:
        # Check if this client is not the sender
        if client != sender:
            try:
                await client.websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                # Remove client from the list of connected clients
                await disconnect(client)

# Connect client to the server
async def connect(client):
    clients.add(client)
    logging.info(f"{client.remote_address} connected.")
    await broadcast(f"{client.remote_address} connected.", client)

# Disconnect client from the server
async def disconnect(client):
    clients.discard(client)
    try:
        await broadcast(f"{client.remote_address} disconnected.", client)
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"{client.remote_address} disconnected.")

# Main function to run the server
async def main():
    async with websockets.serve(handler, "127.0.0.1", 8888):
        await asyncio.Future()

# Run the server
asyncio.run(main())
