import os
import requests
from flask import Flask, request
from PIL import Image

# === Your Telegram bot token (embedded directly) ===
TELEGRAM_BOT_TOKEN = "8207816126:AAG7X3wNVGtZKVLe7STeF40HxYc6Q_je0RU"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

app = Flask(__name__)

# === Use Pillow to check image type ===
def get_image_type(path):
    try:
        with Image.open(path) as img:
            return img.format.lower()  # e.g., 'jpeg', 'png'
    except Exception:
        return None

# === Send message to user ===
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

# === Main webhook endpoint ===
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    chat_id = message["chat"]["id"]

    # === Handle image (photo) messages ===
    if "photo" in message:
        photo_sizes = message["photo"]
        largest_photo = photo_sizes[-1]
        file_id = largest_photo["file_id"]

        # Get file path from Telegram
        file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

        # Download the image
        file_data = requests.get(file_url)
        temp_filename = "temp_img"

        with open(temp_filename, "wb") as f:
            f.write(file_data.content)

        # Detect image type
        img_type = get_image_type(temp_filename)
        os.remove(temp_filename)

        if img_type in ["jpeg", "png"]:
            send_message(chat_id, f"✅ Received a valid {img_type.upper()} image.")
        else:
            send_message(chat_id, "❌ Unsupported image type.")

    else:
        send_message(chat_id, "Please send an image.")

    return "ok"

# === Test route to see if bot is running ===
@app.route("/", methods=["GET"])
def index():
    return "Webhook bot running!"

if __name__ == "__main__":
    app.run(debug=True)