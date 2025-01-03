import asyncio
import logging
from controllers.app import App
from helpers.app import get_json_file_content, storage_path, is_auth, do_login, HASS_TOKEN, MY_PASSWORD
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from controllers.ha import HomeAssistant
from user_agents import parse
from datetime import datetime

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

ha = HomeAssistant()
app = Flask(__name__)
socketio = SocketIO(app)

@app.get('/')
def home():
    return render_template("pages/index.html")

@app.get('/<path1>')
def path1(path1):
    return render_template("pages/index.html")

@app.get('/backend/entities')
def entities():
    ents = get_json_file_content(storage_path('entities.json'))
    return jsonify({'status': 1, 'data': ents})

@app.get('/backend/log')
def log():
    ents = get_json_file_content(storage_path('log.json'))
    return jsonify({'status': 1, 'data': ents})

@app.post('/backend/set-state')
def state():
    local_app = App()
    resp = local_app.update_entity(request.json)
    if resp:
        local_app.entities()  # Force an update to entities.json after changing state
        return jsonify({'status': True}), 200
    return jsonify({'status': False}), 400

@app.post('/backend/api')
def api():
    local_app = App()
    resp = local_app.api(request.json)
    return jsonify({'status': resp}), 200 if resp else 400

@app.post('/backend/do-login')
def login():
    if request.json['password'] != MY_PASSWORD:
        return jsonify({'status': False}), 401
    ua = request.headers.get('User-Agent')
    user_agent = parse(ua)
    do_login(request.json['device_id'])
    return jsonify({'status': True, 'data': {'os': user_agent.os.family.lower(), 'is_touch': user_agent.is_mobile or user_agent.is_tablet}}), 200

@app.post('/backend/auth-token')
def get_auth():
    ua = request.headers.get('User-Agent')
    user_agent = parse(ua)
    if HASS_TOKEN is not None:
        local_app = App()
        resp = local_app.api()
        if resp and is_auth(request.json['device_id']):
            return jsonify({'status': True, 'data': {'os': user_agent.os.family.lower(), 'is_touch': user_agent.is_mobile or user_agent.is_tablet}}), 200
        else:
            return jsonify({'status': False, 'data': {'os': user_agent.os.family.lower(), 'is_touch': user_agent.is_mobile or user_agent.is_tablet}}), 400
    else:
        return jsonify({'status': False, 'data': {'os': user_agent.os.family.lower()}}), 400

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('set_state')
def handle_set_state(data):
    print(f"Set state: {data}")
    asyncio.run(ha.call_service(data['domain'], data['service'], data['service_data']))

async def periodic_polling():
    while True:
        try:
            current_time = datetime.now()
            if (current_time - ha.last_poll_time).seconds > 60:
                local_app = App()
                local_app.entities()
                ha.last_poll_time = current_time
        except Exception as e:
            print(f"Error during periodic polling: {e}")
        await asyncio.sleep(60)  # Poll every 60 seconds

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(periodic_polling())
    try:
        socketio.run(app, host='0.0.0.0', port=4100, debug=False, allow_unsafe_werkzeug=True)
    finally:
        tasks = asyncio.all_tasks(loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()