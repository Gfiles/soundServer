from PIL import Image
import os

SRC = os.path.join(os.path.dirname(__file__), 'soundsync_icon.png')
ICO_PATH = os.path.join(os.path.dirname(__file__), 'icon.ico')
PNG_PATH = os.path.join(os.path.dirname(__file__), 'icon.png')

if not os.path.exists(SRC):
    # Fallback if source icon is missing: generate a simple blue circle
    from PIL import ImageDraw
    img = Image.new('RGBA', (256, 256), (15, 23, 42, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, 236, 236], fill=(56, 189, 248, 255))
else:
    img = Image.open(SRC).convert('RGBA')

# Save multi-resolution ICO
sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
img.save(ICO_PATH, format='ICO', sizes=sizes)
print(f"ICO saved: {ICO_PATH}")

# Save PNG for UI/Tray
img.resize((64, 64), Image.LANCZOS).save(PNG_PATH, format='PNG')
print(f"PNG saved: {PNG_PATH}")

# Copy to client/assets for runtime access
assets_dir = os.path.join(os.path.dirname(__file__), 'client', 'assets')
os.makedirs(assets_dir, exist_ok=True)
import shutil
shutil.copy2(PNG_PATH, os.path.join(assets_dir, 'icon.png'))
