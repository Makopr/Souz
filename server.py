import asyncio
import websockets

connected_clients = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            # Broadcast the received message to all connected clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
                    print("Frame broadcasted to client")
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "26.248.111.145", 3306):
        print("Server started on ws://localhost:8766")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
