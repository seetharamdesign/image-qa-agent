# utils/image_utils.py

import base64
from PIL import Image
import io


def load_and_encode_image(image_path: str) -> tuple[str, str]:
    """
    Opens an image, resizes if needed, and returns
    a base64 encoded string + media type for Claude API.
    """
    image = Image.open(image_path)

    # Convert to RGB if needed (handles PNG transparency, grayscale etc.)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize if larger than Claude's optimal size
    max_size = 5000
    if max(image.width, image.height) > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)

    # Save to memory buffer instead of disk
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)

    # Encode to base64
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    media_type = "image/jpeg"

    return encoded, media_type
