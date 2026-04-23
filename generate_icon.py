"""
generate_icon.py
Run this once to produce client/assets/icon.ico from the source PNG.
Requires Pillow: pip install Pillow
"""
from PIL import Image
import os

SRC = os.path.join(os.path.dirname(__file__), 'soundsync_icon.png')
DEST_DIR = os.path.join(os.path.dirname(__file__), 'client', 'assets')
DEST_ICO = os.path.join(DEST_DIR, 'icon.ico')
DEST_PNG = os.path.join(DEST_DIR, 'icon.png')

os.makedirs(DEST_DIR, exist_ok=True)

img = Image.open(SRC).convert('RGBA')

# Save multi-resolution ICO (Windows standard sizes)
sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
img.save(DEST_ICO, format='ICO', sizes=sizes)
print(f"ICO saved: {DEST_ICO}")

# Also save a 64x64 PNG for the in-process pystray tray icon
img.resize((64, 64), Image.LANCZOS).save(DEST_PNG, format='PNG')
print(f"PNG saved: {DEST_PNG}")
