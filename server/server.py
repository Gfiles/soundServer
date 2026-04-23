import os
import uuid
import hashlib
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from database import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'soundsync_secret'
app.config['UPLOAD_FOLDER'] = 'media'
# threading mode: no eventlet/gevent required, fully compatible with Waitress
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Ensure media folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/clients')
def get_clients():
    return jsonify(db.get_clients_enriched())

@app.route('/api/media', methods=['GET', 'POST'])
def manage_media():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Calculate hash
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        
        media_id = str(uuid.uuid4())
        db.add_media(media_id, filename, filename, file_hash)
        return jsonify({'id': media_id, 'filename': filename, 'hash': file_hash})
    
    return jsonify(db.get_media())

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# WebSocket Events
@socketio.on('register')
def handle_register(data):
    client_id = data.get('client_id')
    name = data.get('name')
    if client_id:
        join_room(client_id)
        db.update_client(client_id, name=name)
        # Send current config to client
        config = db.get_client_config(client_id)
        emit('sync_config', config, room=client_id)
        print(f"Client registered: {name} ({client_id})")

@socketio.on('status_update')
def handle_status(data):
    client_id = data.get('client_id')
    if client_id:
        # Cache the latest status in the database object (in-memory)
        db.update_client_status(client_id, data)
        # Broadcast to dashboard
        socketio.emit('ui_update', data)

@socketio.on('control_playback')
def handle_control(data):
    # data: {client_id, action, channel}
    client_id = data.get('client_id')
    if client_id:
        emit('cmd_playback', data, room=client_id)

@socketio.on('set_volume')
def handle_volume(data):
    # data: {client_id, channel, level}
    client_id = data.get('client_id')
    if client_id:
        db.update_client(client_id, volumes={str(data['channel']): data['level']})
        emit('cmd_volume', data, room=client_id)

@socketio.on('update_mapping')
def handle_mapping(data):
    # data: {client_id, channels: {1: media_id, ...}}
    client_id = data.get('client_id')
    channels = data.get('channels')
    if client_id and channels:
        db.update_client(client_id, channels=channels)
        # Push new config to client to trigger sync/download
        config = db.get_client_config(client_id)
        emit('sync_config', config, room=client_id)
        
        # Also notify UI of the name change
        enriched = db.get_clients_enriched().get(client_id)
        if enriched:
            socketio.emit('ui_update', {
                'client_id': client_id,
                'channel_media_names': enriched['channel_media_names']
            })
        print(f"Updated mapping for {client_id}")

if __name__ == '__main__':
    print("Starting SoundSync Server on http://0.0.0.0:6060")
    # NOTE: Waitress does not support WebSocket upgrades (it is WSGI-only).
    # socketio.run() with async_mode='threading' is the correct approach:
    # it uses Werkzeug's multi-threaded server which handles both HTTP and
    # WebSocket on the same port with zero external dependencies.
    socketio.run(
        app,
        host='0.0.0.0',
        port=6060,
        debug=False,
        allow_unsafe_werkzeug=True,   # Required for Flask-SocketIO >= 5 without eventlet/gevent
        use_reloader=False,           # Prevent double-start
        log_output=True
    )
