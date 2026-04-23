import os
import sys
import uuid
import socket
import toml
import requests
import hashlib
import time
import threading
import socketio
import webbrowser
from pystray import Icon, Menu, MenuItem
from PIL import Image
from audio_engine import audio_engine


def ensure_singleton():
    """Ensure only one instance of the client is running using a local socket."""
    try:
        # We store the socket in a global variable to keep it open
        global _singleton_socket
        _singleton_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _singleton_socket.bind(('127.0.0.1', 6061))
    except socket.error:
        print("Error: Another instance of SoundSync Client is already running.")
        sys.exit(1)


SERVER_URL = "http://localhost:6060" # Default, updated at runtime
CONFIG_FILE = 'client_config.toml'
MEDIA_DIR = 'media'

class SoundSyncClient:
    def __init__(self):
        self.config = self.load_config()
        self.client_id = self.config['client_id']
        self.pc_name = self.config['pc_name']
        
        global SERVER_URL
        SERVER_URL = self.config.get('server_url', "http://localhost:6060")
        
        self.sio = socketio.Client()
        self.setup_sio()
        
        if not os.path.exists(MEDIA_DIR):
            os.makedirs(MEDIA_DIR)
        
        # Resume immediately for offline support
        self.resume_last_state()

    def prompt_for_server_ip(self):
        """Show a GUI popup to ask for the server IP on first run."""
        import tkinter as tk
        from tkinter import simpledialog
        
        root = tk.Tk()
        root.withdraw()
        
        # Bring to front
        root.attributes("-topmost", True)
        
        ip = simpledialog.askstring(
            "SoundSync Setup", 
            "Enter the Server IP address (e.g., 192.168.1.50):",
            initialvalue="localhost"
        )
        root.destroy()
        
        if not ip:
            print("Setup cancelled. Exiting.")
            sys.exit(0)
            
        return f"http://{ip}:6060"

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            config = toml.load(CONFIG_FILE)
            # Ensure defaults for missing keys
            if 'client_id' not in config: config['client_id'] = str(uuid.uuid4())
            if 'pc_name' not in config: config['pc_name'] = socket.gethostname()
            if 'server_url' not in config: config['server_url'] = "http://localhost:6060"
            if 'last_state' not in config: config['last_state'] = {'channels': {}, 'volumes': {}}
            return config
        else:
            # First run: Ask for IP
            server_url = self.prompt_for_server_ip()
            
            new_config = {
                'client_id': str(uuid.uuid4()),
                'pc_name': socket.gethostname(),
                'server_url': server_url,
                'last_state': {'channels': {}, 'volumes': {}}
            }
            self.save_config(new_config)
            return new_config

    def save_config(self, config=None):
        if config: self.config = config
        with open(CONFIG_FILE, 'w') as f:
            toml.dump(self.config, f)

    def resume_last_state(self):
        """Resume playback from the last known state saved locally."""
        state = self.config.get('last_state', {})
        channels = state.get('channels', {})
        volumes = state.get('volumes', {})
        
        if channels:
            print("Resuming last known state (Offline Mode)...")
            for ch, info in channels.items():
                filename = info['filename']
                local_path = os.path.join(MEDIA_DIR, filename)
                if os.path.exists(local_path):
                    audio_engine.play(ch, local_path)
                    vol = volumes.get(str(ch), 100)
                    audio_engine.set_volume(ch, vol)

    def setup_sio(self):
        @self.sio.on('connect')
        def on_connect():
            print("Connected to server.")
            self.sio.emit('register', {
                'client_id': self.client_id,
                'name': self.pc_name
            })

        @self.sio.on('sync_config')
        def on_sync(data):
            # data: {name, channels: {1: {filename, hash, volume}, ...}}
            if data:
                threading.Thread(target=self.sync_media, args=(data['channels'],)).start()

        @self.sio.on('cmd_playback')
        def on_playback(data):
            action = data['action']
            channel = data['channel']
            if action == 'play': audio_engine.resume(channel)
            elif action == 'pause': audio_engine.pause(channel)
            elif action == 'restart': audio_engine.restart(channel)

        @self.sio.on('cmd_volume')
        def on_volume(data):
            ch = str(data['channel'])
            lvl = int(data['level'])
            audio_engine.set_volume(ch, lvl)
            
            # Persist volume change
            if 'volumes' not in self.config['last_state']: self.config['last_state']['volumes'] = {}
            self.config['last_state']['volumes'][ch] = lvl
            self.save_config()

    def sync_media(self, channels):
        print("Syncing media...")
        for ch, info in channels.items():
            filename = info['filename']
            expected_hash = info['hash']
            local_path = os.path.join(MEDIA_DIR, filename)
            
            # Check if exists and hash matches
            if os.path.exists(local_path):
                sha256_hash = hashlib.sha256()
                with open(local_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                if sha256_hash.hexdigest() == expected_hash:
                    print(f"File {filename} is up to date.")
                    audio_engine.play(ch, local_path)
                    audio_engine.set_volume(ch, info['volume'])
                    # Update local state
                    self.config['last_state']['channels'][str(ch)] = info
                    self.config['last_state']['volumes'][str(ch)] = info['volume']
                    continue

            # Download
            print(f"Downloading {filename}...")
            r = requests.get(f"{SERVER_URL}/media/{filename}")
            if r.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(r.content)
                audio_engine.play(ch, local_path)
                audio_engine.set_volume(ch, info['volume'])
                # Update local state
                self.config['last_state']['channels'][str(ch)] = info
                self.config['last_state']['volumes'][str(ch)] = info['volume']
        
        self.save_config()

    def run_sio(self):
        while True:
            try:
                if not self.sio.connected:
                    self.sio.connect(SERVER_URL)
                time.sleep(10)
            except Exception as e:
                print(f"Connection error: {e}")
                time.sleep(10)

    def send_heartbeat(self):
        while True:
            if self.sio.connected:
                # Collect status from all channels
                status = {
                    'client_id': self.client_id,
                    'status': 'online',
                    'channels': {}
                }
                for ch in audio_engine.players:
                    status['channels'][ch] = audio_engine.get_status(ch)
                self.sio.emit('status_update', status)
            time.sleep(2)

def create_image():
    """Load the real icon from assets, fall back to a generated one."""
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    icon_path = os.path.join(assets_dir, 'icon.png')
    if os.path.exists(icon_path):
        return Image.open(icon_path).convert('RGBA')
    # Fallback: generate a simple coloured circle
    from PIL import ImageDraw
    img = Image.new('RGBA', (64, 64), (15, 23, 42, 255))
    ImageDraw.Draw(img).ellipse([8, 8, 56, 56], fill=(56, 189, 248, 255))
    return img

def on_settings(icon, item):
    webbrowser.open(f"{SERVER_URL}/settings")

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

if __name__ == "__main__":
    # Ensure only one instance
    ensure_singleton()

    client = SoundSyncClient()

    # Start background threads
    threading.Thread(target=client.run_sio, daemon=True).start()
    threading.Thread(target=client.send_heartbeat, daemon=True).start()

    # System Tray
    tray_icon = Icon("SoundSync", create_image(), "SoundSync", menu=Menu(
        MenuItem("Settings", on_settings),
        MenuItem("Exit", on_exit)
    ))

    print("SoundSync Client is running in the system tray.")
    tray_icon.run()
