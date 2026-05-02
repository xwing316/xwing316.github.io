#!/usr/bin/env python3
"""Generate game thumbnail images using LocalAI Flux model."""

import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

LOCALAI_URL = os.getenv("LOCALAI_URL", "http://192.168.86.2:3033/v1/images/generations")
MODEL = os.getenv("IMAGE_MODEL", "flux.2-klein-9b")
OUTPUT_DIR = "/home/shane/github-site/assets/images"

def generate_image(prompt: str, output_path: str, size: str = "1024x768"):
    """Generate an image using LocalAI Flux and save to file."""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        LOCALAI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    image_data = data.get("data", [{}])[0]
    b64 = image_data.get("b64_json") or ""

    # Handle data: URI
    if not b64 and image_data.get("url", "").startswith("data:"):
        b64 = image_data["url"].split(",", 1)[1]

    # Handle regular URL — download the image
    img_url = image_data.get("url", "")
    if not b64 and img_url and not img_url.startswith("data:"):
        print(f"Downloading image from URL...")
        img_req = urllib.request.Request(img_url)
        with urllib.request.urlopen(img_req, timeout=60) as img_resp:
            img_bytes = img_resp.read()
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            size_kb = len(img_bytes) / 1024
            print(f"SAVED:{output_path} ({size_kb:.0f}KB)")
            return output_path

    if not b64:
        raise ValueError(f"No image data in response. Keys: {list(image_data.keys())}")

    img_bytes = base64.b64decode(b64)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_bytes)

    size_kb = len(img_bytes) / 1024
    print(f"SAVED:{output_path} ({size_kb:.0f}KB)")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_thumbnails.py <prompt> <output_path> [size]")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2]
    size = sys.argv[3] if len(sys.argv) > 3 else "1024x768"

    try:
        generate_image(prompt, output_path, size)
    except Exception as e:
        print(f"ERROR:{e}")
        sys.exit(1)