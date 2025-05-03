
# client.py
import websockets
import asyncio

from aioconsole import ainput

async def retrieve_messages(websocket):
    while True:
        try:
            message = await websocket.recv()
            print(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed.")
            break

async def send_messages(websocket):
    while True:
        try:
            message = await ainput()
            if not message:
                return
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed.")
            break

async def main():
    async with websockets.connect("ws://127.0.0.1:8888") as websocket:
        await asyncio.gather(
            retrieve_messages(websocket),
            send_messages(websocket)
        )

asyncio.run(main())
