from PIL import Image
import os

# Source path (Artifact)
src = r"C:/Users/SK_Park/.gemini/antigravity/brain/c3353d80-8c1e-4aa1-8963-a005208187e7/tomato_icon_1767034404745.png"
dst_ico = "assets/icon.ico"
dst_png = "assets/icon.png"

if os.path.exists(src):
    img = Image.open(src)
    # Resize to standard icon sizes
    img.save(dst_ico, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    img.save(dst_png, format='PNG')
    print("Icon created successfully.")
else:
    print(f"Source image not found at {src}")
