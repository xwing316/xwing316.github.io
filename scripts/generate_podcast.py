#!/usr/bin/env python3
"""
Generate a podcast MP3 from a script file using Azure DragonHD TTS.
Splits long scripts into chunks, generates audio per chunk, then concatenates.

Usage:
    python generate_podcast.py script.json output.mp3

script.json format:
{
  "title": "Episode Title",
  "hosts": {
    "Alex": "en-US-Andrew:DragonHDLatestNeural",
    "Jordan": "en-US-Emma:DragonHDLatestNeural"
  },
  "lines": [
    {"speaker": "Alex", "text": "Welcome to the show!"},
    {"speaker": "Jordan", "text": "Thanks for having me."}
  ]
}
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests


def load_env(path="~/.hermes/.env"):
    env_path = os.path.expanduser(path)
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Env file not found: {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def generate_ssml_chunk(chunk_lines, hosts):
    """Build SSML for a chunk of lines."""
    voice_segments = []
    for line in chunk_lines:
        speaker = line["speaker"]
        text = line["text"]
        voice = hosts.get(speaker, "en-US-Andrew:DragonHDLatestNeural")
        # Escape XML
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        voice_segments.append(f'<voice name="{voice}">{safe}</voice>')

    voices_ssml = "".join(voice_segments)
    ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">{voices_ssml}</speak>'
    return ssml


def tts_request(ssml, output_path):
    """Call Azure TTS REST API."""
    load_env()
    key = os.environ.get("AZURE_SPEECH_KEY")
    region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
    if not key:
        raise RuntimeError("AZURE_SPEECH_KEY not found in ~/.hermes/.env")

    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-24khz-160kbitrate-mono-mp3",
    }

    resp = requests.post(url, headers=headers, data=ssml.encode("utf-8"))
    if resp.status_code != 200:
        raise RuntimeError(f"Azure TTS failed: {resp.status_code} - {resp.text[:500]}")

    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path


def chunk_lines(lines, max_chars=8000):
    """Split lines into chunks where SSML stays under max_chars."""
    chunks = []
    current = []
    current_len = 0
    # Base SSML overhead ~100 chars
    overhead = 100

    for line in lines:
        # Approximate length: voice tag + text + close tag
        line_ssml_len = len(line["text"]) + 80
        if current and current_len + line_ssml_len > max_chars:
            chunks.append(current)
            current = [line]
            current_len = line_ssml_len + overhead
        else:
            current.append(line)
            current_len += line_ssml_len

    if current:
        chunks.append(current)

    return chunks


def concatenate_mp3s(mp3_paths, output_path):
    """Concatenate MP3 files using ffmpeg."""
    if len(mp3_paths) == 1:
        os.rename(mp3_paths[0], output_path)
        return

    # Create concat list file
    list_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    for p in mp3_paths:
        list_file.write(f"file '{os.path.abspath(p)}'\n")
    list_file.close()

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file.name,
        "-acodec", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(list_file.name)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed: {result.stderr}")


def generate_podcast(script_path, output_path):
    with open(script_path) as f:
        data = json.load(f)

    hosts = data["hosts"]
    lines = data["lines"]

    print(f"Generating podcast: {data.get('title', 'Untitled')}")
    print(f"Total lines: {len(lines)}")

    chunks = chunk_lines(lines)
    print(f"Split into {len(chunks)} chunks")

    mp3_files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(tmpdir, f"chunk_{i:03d}.mp3")
            ssml = generate_ssml_chunk(chunk, hosts)
            print(f"  Chunk {i+1}/{len(chunks)} ({len(ssml)} chars)...")
            tts_request(ssml, chunk_path)
            mp3_files.append(chunk_path)

        print(f"Concatenating {len(mp3_files)} chunks...")
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        concatenate_mp3s(mp3_files, output_path)

    print(f"Done: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_podcast.py script.json output.mp3")
        sys.exit(1)
    generate_podcast(sys.argv[1], sys.argv[2])
