
# server.py
import websockets
import asyncio

clients = set()

async def handler(websocket):
    await connect(websocket)
    try:
        # Listen for incoming messages
        async for message in websocket:
            await broadcast(message, websocket)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove client from the list of connected clients
        await disconnect(websocket)

# Broadcast message to all connected clients except the sender
async def broadcast(message, websocket):
    for client in clients:
        if client != websocket:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                # Remove client from the list of connected clients
                await disconnect(client)

# Connect client to the server
async def connect(websocket):
    clients.add(websocket)
    await broadcast(f"{websocket.remote_address} connected.", websocket)

# Disconnect client from the server
async def disconnect(websocket):
    clients.discard(websocket)
    try:
        await broadcast(f"{websocket.remote_address} disconnected.", websocket)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await websocket.close()

# Main function to run the server
async def main():
    async with websockets.serve(handler, "127.0.0.1", 8888):
        await asyncio.Future()

# Run the server
asyncio.run(main())
