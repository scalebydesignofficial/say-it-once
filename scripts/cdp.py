"""Tiny Chrome DevTools client using only the standard library.

Lets us open a page once and grab hundreds of frames quickly, which is how animated
carousels are recorded. Works with Chrome, Edge, Brave, or Chromium.
"""
import base64
import json
import os
import pathlib
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request

import engine_lib as E


class WS:
    def __init__(self, host, port, path):
        self.s = socket.create_connection((host, port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RuntimeError("Browser closed the connection")
            buf += chunk
        if b" 101 " not in buf.split(b"\r\n", 1)[0] + b" ":
            raise RuntimeError("Browser refused the debugging connection")
        self.rest = buf.split(b"\r\n\r\n", 1)[1]

    def _recvn(self, n):
        out = b""
        if self.rest:
            out, self.rest = self.rest[:n], self.rest[n:]
        while len(out) < n:
            chunk = self.s.recv(min(1 << 20, n - len(out)))
            if not chunk:
                raise RuntimeError("Browser closed the connection")
            out += chunk
        return out

    def send(self, text):
        payload = text.encode()
        n = len(payload)
        head = bytearray([0x81])
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126)
            head += struct.pack(">H", n)
        else:
            head.append(0x80 | 127)
            head += struct.pack(">Q", n)
        mask = os.urandom(4)
        head += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload)) if n < 4096 else _xor(payload, mask)
        self.s.sendall(bytes(head) + masked)

    def recv(self):
        data = b""
        while True:
            b1, b2 = self._recvn(2)
            fin, op = b1 & 0x80, b1 & 0x0F
            ln = b2 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._recvn(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._recvn(8))[0]
            payload = self._recvn(ln) if ln else b""
            if op == 8:
                raise RuntimeError("Browser closed the connection")
            if op in (9, 10):
                continue
            data += payload
            if fin:
                return data.decode("utf-8", "replace")

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


def _xor(payload, mask):
    # fast masking for big messages
    n = len(payload)
    full = (mask * (n // 4 + 1))[:n]
    return (int.from_bytes(payload, "big") ^ int.from_bytes(full, "big")).to_bytes(n, "big")


class Browser:
    def __init__(self, width, height):
        chrome = E.find_chrome()
        if not chrome:
            raise RuntimeError("No Chrome, Edge, Brave, or Chromium found.")
        self.profile = tempfile.mkdtemp(prefix="engine-cdp-")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--disable-extensions", "--allow-file-access-from-files",
               "--force-device-scale-factor=1", "--disable-dev-shm-usage", "--remote-debugging-port=0",
               f"--user-data-dir={self.profile}", f"--window-size={width},{height}", "about:blank"]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.append("--no-sandbox")
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = pathlib.Path(self.profile) / "DevToolsActivePort"
        for _ in range(150):
            if port_file.exists() and len(port_file.read_text().split()) >= 1:
                break
            time.sleep(0.1)
        else:
            self.close()
            raise RuntimeError("Browser did not start")
        self.port = int(port_file.read_text().split()[0])
        ws_path = None
        for _ in range(60):
            try:
                pages = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=5))
                pages = [p for p in pages if p.get("type") == "page"]
                if pages:
                    ws_path = "/" + pages[0]["webSocketDebuggerUrl"].split("/", 3)[3]
                    break
            except Exception:
                pass
            time.sleep(0.1)
        if not ws_path:
            self.close()
            raise RuntimeError("Could not attach to the browser")
        self.ws = WS("127.0.0.1", self.port, ws_path)
        self._id = 0
        self.call("Page.enable")
        self.call("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=False)

    def call(self, method, **params):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error'].get('message')}")
                return msg.get("result", {})

    def eval(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")

    def open(self, path, timeout=30):
        self.call("Page.navigate", url=pathlib.Path(path).resolve().as_uri())
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.eval("document.documentElement.getAttribute('data-ready')") == "1":
                return
            time.sleep(0.1)
        raise RuntimeError("Page did not finish loading")

    def frame(self, quality=92):
        r = self.call("Page.captureScreenshot", format="jpeg", quality=quality, fromSurface=True)
        return base64.b64decode(r["data"])

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass
        shutil.rmtree(self.profile, ignore_errors=True)
