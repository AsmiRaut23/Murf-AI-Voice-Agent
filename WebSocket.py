# from flask import Flask
# from flask_sock import Sock

# app = Flask(__name__)
# sock = Sock(app)

# @sock.route('/ws')
# def ws_handler(ws):
#     while True:
#         data = ws.receive()
#         if data is None:
#             break
#         print(f"Received via WS: {data}")
#         ws.send(f"Echo: {data}")

# if __name__ == "__main__":
#     app.run(debug=True)






from flask import Flask, render_template
from flask_sock import Sock
import os
from datetime import datetime

app = Flask(__name__)
sock = Sock(app)

# Ensure a recordings/ folder exists
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

def new_filename(ext=".webm"):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(RECORDINGS_DIR, f"recording-{ts}{ext}")

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("WebSocket.html")

@sock.route('/ws')
def ws_handler(ws):
    print("WS client connected")

    # Default to a .webm file (works well with MediaRecorder in browser)
    filepath = new_filename(".webm")
    f = open(filepath, "wb")
    print(f"Saving audio to: {filepath}")

    try:
        while True:
            msg = ws.receive()
            if msg is None:
                print("WS client disconnected")
                break

            # Handle text messages
            if isinstance(msg, str):
                print(f"WS text received: {msg}")

                # Optional: let client set the extension early (e.g., "mime:audio/ogg")
                if msg.startswith("mime:"):
                    mime = msg.split(":", 1)[1].strip()
                    if f.tell() == 0:  # only switch if file is still empty
                        f.close()
                        ext = ".webm"
                        if "ogg" in mime:
                            ext = ".ogg"
                        elif "wav" in mime:
                            ext = ".wav"
                        elif "mp3" in mime:
                            ext = ".mp3"
                        filepath = new_filename(ext)
                        f = open(filepath, "wb")
                        print(f"Switched file type, saving to: {filepath}")
                else:
                    # Echo text back to client
                    echo_msg = f"Echo: {msg}"
                    ws.send(echo_msg)
                    print(f"Sent echo back: {echo_msg}")

            # Handle binary messages (audio chunks)
            else:
                f.write(msg)
                f.flush()
                print(f"Received {len(msg)} bytes of audio")

    finally:
        f.close()
        print(f"Closed file: {filepath}")

if __name__ == "__main__":
    app.run(debug=True)
