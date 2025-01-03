import asyncio
import websockets
import threading
import time
import requests
from helpers.app import *
from controllers.app import App
import signal
import sys
import random
from datetime import datetime

app = App()

class HomeAssistant:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HomeAssistant, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        self.connection = None
        self.is_connected = False
        self.error_count = 0
        self.ping_interval = 30
        self.ping_timeout = 10
        self.last_poll_time = datetime.now()
        self.reconnect_task = None
        self.shutdown_flag = asyncio.Event()

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_asyncio_loop)
        self.thread.start()

        # Handle graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: self.initiate_shutdown())
        signal.signal(signal.SIGTERM, lambda s, f: self.initiate_shutdown())

    def wait_for_home_assistant(self):
        while True:
            try:
                response = requests.get(HASS_API, headers={"Authorization": f"Bearer {HASS_TOKEN}"})
                if response.status_code == 200:
                    print("Home Assistant is available.")
                    return True
                else:
                    print(f"Waiting for Home Assistant to be available (status: {response.status_code})...")
            except requests.ConnectionError:
                print("Home Assistant is not available yet. Retrying in 5 seconds...")
            time.sleep(5)  # Wait for 5 seconds before retrying

    async def connect_to_home_assistant(self):
        self.wait_for_home_assistant()
        try:
            async with websockets.connect(HASS_URL) as websocket:
                self.connection = websocket
                try:
                    await websocket.send(json.dumps({
                        "type": "auth",
                        "access_token": HASS_TOKEN
                    }))
                    print("Connection successful")
                    self.is_connected = True
                    self.reconnect_task = None
                except Exception as e:
                    print(f"Failed to connect: {e}")
                    self.is_connected = False

                await self.handle_messages(websocket)
        except asyncio.CancelledError:
            print("WebSocket connection closed.")
            raise
        except Exception as e:
            print(f"Exception in connect_to_home_assistant: {e}")

    async def handle_messages(self, websocket):
        try:
            async for message in websocket:
                if self.shutdown_flag.is_set():
                    break
                data = json.loads(message)
                if data.get('type') == 'auth_invalid':
                    log_error(True)
                elif data.get('type') == 'auth_ok':
                    log_error(False)
                    print("Authenticated successfully")
                    app.entities()
                    await websocket.send(json.dumps({"id": 1, "type": "subscribe_events"}))
                    asyncio.create_task(self.ping_pong(websocket))
                elif data.get('type') == "event":
                    if data['event']['event_type'] == "state_changed":
                        app.entities()
                else:
                    log_error(False)
                    global home_assistant_data
                    home_assistant_data = data
        except asyncio.CancelledError:
            print("handle_messages cancelled.")
            raise
        except Exception as e:
            if not self.shutdown_flag.is_set():
                self.error_count += 1
                if self.error_count > 2:
                    log_error(False)
                await asyncio.sleep(2)
                print(f"Connection closed unexpectedly: {e}. Reconnecting...")
                if not self.reconnect_task or self.reconnect_task.done():
                    self.reconnect_task = asyncio.create_task(self.reconnect_with_backoff())

    async def ping_pong(self, websocket):
        while True:
            try:
                await websocket.ping()
                await asyncio.sleep(self.ping_interval)
            except asyncio.TimeoutError:
                print("Ping timeout. Reconnecting...")
                if not self.reconnect_task or self.reconnect_task.done():
                    self.reconnect_task = asyncio.create_task(self.reconnect_with_backoff())
                break
            if self.shutdown_flag.is_set():
                break

    async def reconnect_with_backoff(self):
        initial_wait = 1
        max_wait = 32
        while not self.is_connected:
            wait_time = min(initial_wait * 2, max_wait) + random.uniform(0, 1)
            print(f"Attempting to reconnect in {wait_time:.2f} seconds...")
            await asyncio.sleep(wait_time)
            await self.connect_to_home_assistant()
            initial_wait = wait_time

    def run_asyncio_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.connect_to_home_assistant())
        except asyncio.CancelledError:
            print("run_asyncio_loop cancelled.")

    async def call_service(self, room):
        if self.connection:
            resp = await self.connection.send(json.dumps({
                "type": "call_service",
                "domain": "homeassistant",
                "service": "toggle",
                "service_data": {"entity_id": f"input_boolean.{room}"},
                "target": {"entity_id": f"input_boolean.{room}"},
            }))
            print(f"Service call response: {resp}")

    async def close_connection(self):
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            print("WebSocket connection closed.")

    async def shutdown(self):
        print("Shutting down gracefully...")
        self.shutdown_flag.set()
        await self.close_connection()
        tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task(self.loop)]
        [task.cancel() for task in tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()
        return results

    def initiate_shutdown(self):
        asyncio.run_coroutine_threadsafe(self.shutdown(), self.loop)