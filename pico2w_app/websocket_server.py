from machine import Pin
import asyncio
from microdot import Microdot
from microdot.websocket import with_websocket

from message_manager import message_manager

pin = Pin("LED", Pin.OUT)

app = Microdot()

@app.route('/ws')
@with_websocket
async def echo(request, ws):
    print(f"websocket_server: Client {request.client_addr[0]} connected to websocket")
    while True:
        data = await ws.receive()
        
        message_manager.process_message(data)

        if "led" in data:
            pin.toggle()
            
        await ws.send(data)

async def start_websocket_server():
    server = asyncio.create_task(app.start_server(port=80))
    print(f"websocket_server: Started websocket server, listening")

    await server