import toml
import os

DB_FILE = 'config.toml'

class Database:
    def __init__(self):
        self.data = {
            'clients': {},  # client_id: {name, channels: {1: media_id}, volumes: {1: 100}}
            'media': {},    # media_id: {name, filename, hash}
            'settings': {
                'port': 6060
            }
        }
        self.load()

    def load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    self.data = toml.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")

    def save(self):
        try:
            # We use toml.dump to save. 
            # Note: standard 'toml' library doesn't easily preserve comments on write,
            # but it creates a valid TOML file.
            with open(DB_FILE, 'w') as f:
                f.write("# SoundSync Configuration File\n")
                f.write("# This file stores client mappings and media metadata\n\n")
                toml.dump(self.data, f)
        except Exception as e:
            print(f"Error saving database: {e}")

    def get_clients_enriched(self):
        clients = self.data.get('clients', {})
        media_list = self.data.get('media', {})
        enriched = {}
        for c_id, c in clients.items():
            c_copy = c.copy()
            # Add media names to the channels
            c_copy['channel_media_names'] = {}
            for ch, m_id in c.get('channels', {}).items():
                m = media_list.get(m_id)
                c_copy['channel_media_names'][ch] = m['name'] if m else "No Media"
            enriched[c_id] = c_copy
        return enriched

    def get_clients(self):
        return self.data.get('clients', {})

    def update_client(self, client_id, name=None, channels=None, volumes=None):
        if 'clients' not in self.data: self.data['clients'] = {}
        
        if client_id not in self.data['clients']:
            self.data['clients'][client_id] = {
                'name': name or f"Client {client_id[:6]}",
                'channels': channels or {},
                'volumes': volumes or {},
                'status': 'offline'
            }
        else:
            if name: self.data['clients'][client_id]['name'] = name
            if channels: 
                if 'channels' not in self.data['clients'][client_id]:
                    self.data['clients'][client_id]['channels'] = {}
                self.data['clients'][client_id]['channels'].update(channels)
            if volumes: 
                if 'volumes' not in self.data['clients'][client_id]:
                    self.data['clients'][client_id]['volumes'] = {}
                self.data['clients'][client_id]['volumes'].update(volumes)
        self.save()

    def update_client_status(self, client_id, status_data):
        if client_id in self.data.get('clients', {}):
            self.data['clients'][client_id]['status_data'] = status_data
            self.data['clients'][client_id]['status'] = status_data.get('status', 'online')

    def add_media(self, media_id, name, filename, file_hash):
        if 'media' not in self.data: self.data['media'] = {}
        self.data['media'][media_id] = {
            'name': name,
            'filename': filename,
            'hash': file_hash
        }
        self.save()

    def get_media(self):
        return self.data.get('media', {})

    def get_client_config(self, client_id):
        client = self.data.get('clients', {}).get(client_id)
        if not client:
            return None
        
        config = {
            'name': client['name'],
            'channels': {}
        }
        channels = client.get('channels', {})
        volumes = client.get('volumes', {})
        
        for ch, m_id in channels.items():
            media = self.data.get('media', {}).get(m_id)
            if media:
                config['channels'][ch] = {
                    'media_id': m_id,
                    'filename': media['filename'],
                    'hash': media['hash'],
                    'volume': volumes.get(ch, 100)
                }
        return config

db = Database()
