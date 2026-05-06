from microdot import Microdot
import asyncio

from credential_manager import wifi_credential_manager

app = Microdot()

@app.route('/<path:path>')
async def resolver(request, path):
    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>WiFi Configuration</title>
        <style>
            body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #007BFF; color: white; border: none; cursor: pointer; border-radius: 5px; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>WiFi Configuration</h1>
        <form action="/configure" method="POST">
            <label>SSID:</label>
            <input type="text" name="ssid" required>
            <label>Password:</label>
            <input type="password" name="password" required>
            <button type="submit">Save & Connect</button>
        </form>
    </body>
    </html>"""
    return html, 200, {'Content-Type': 'text/html'} 

@app.post('/configure')
async def configure(request):
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    
    if not ssid or not password:
        print(f"captive_portal: No WiFi credentials were submitted to the /configure endpoint")
        return {'Error': 'No WiFi credentials were submitted'}, 400
    
    if not wifi_credential_manager.save_credentials(ssid, password):
        print(f"captive_portal: WiFi credentials could not be saved")
        return {'Error': 'The WiFi credentials could not be saved'}, 400
    
    return {'Success': 'The WiFi credentials were saved'}, 200

@app.route('/')
async def nullpath(request):
    return await resolver(request, '')

async def start_captive_portal():
    server = asyncio.create_task(app.start_server(port=80))
    print(f"captive_portal: Started portal server, waiting for credentials")

    await server