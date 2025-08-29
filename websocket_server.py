# websocket_server.py
from quart import Quart, websocket

app = Quart(__name__)

@app.websocket("/ws")
async def ws():
    while True:
        try:
            message = await websocket.receive()
            await websocket.send(f"Echo: {message}")
        except:
            break  # closes connection if client disconnects
