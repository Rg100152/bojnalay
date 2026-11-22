"""
Capture real UI screenshots with headless Chrome via the DevTools Protocol.
This waits until Flask data has rendered before taking each screenshot.

Usage: python3 capture_screenshots.py http://127.0.0.1:5000
"""

import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

import websocket  # websocket-client

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "assets")
PORT = 9223
PROFILE = "/tmp/bojnalay-cdp-profile"

chrome = subprocess.Popen([
    "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
    "--disable-dev-shm-usage", "--hide-scrollbars", "--force-device-scale-factor=1",
    "--window-size=1440,1120", f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROFILE}", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_for_cdp():
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=1) as response:
                targets = json.load(response)
            page = next(t for t in targets if t.get("type") == "page")
            return page["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Chrome DevTools endpoint did not start")


ws = websocket.create_connection(wait_for_cdp(), timeout=20)
message_id = 0


def send(method, params=None):
    global message_id
    message_id += 1
    ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
    while True:
        reply = json.loads(ws.recv())
        if reply.get("id") == message_id:
            return reply


def evaluate(expression):
    result = send("Runtime.evaluate", {"expression": expression, "returnByValue": True})
    return result.get("result", {}).get("result", {}).get("value")


def shoot(url, filename, ready_selector, ready_count):
    send("Page.navigate", {"url": url})
    for _ in range(80):
        count = evaluate(f"document.querySelectorAll('{ready_selector}').length")
        if isinstance(count, int) and count >= ready_count:
            break
        time.sleep(0.15)
    time.sleep(1.0)  # let fonts and transitions settle
    image = send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
    data = image.get("result", {}).get("data")
    if not data:
        raise RuntimeError(f"Screenshot failed for {filename}: {image}")
    path = os.path.join(ASSETS, filename)
    with open(path, "wb") as handle:
        handle.write(base64.b64decode(data))
    print(f"✅ {path} ({count} '{ready_selector}' elements)")


try:
    send("Page.enable")
    send("Runtime.enable")
    shoot(f"{BASE}/", "screenshot-planner.png", ".meal-slot", 20)
    shoot(f"{BASE}/?view=recipes", "screenshot-recipes.png", ".recipe-card", 8)
finally:
    ws.close()
    chrome.terminate()
    try:
        chrome.wait(timeout=5)
    except subprocess.TimeoutExpired:
        chrome.kill()
