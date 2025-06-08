import os
import requests
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from shutil import copy2

FACEPP_API_KEY = "zRpX_mvGViSiovfRh3-BdXsfKbTDkSyx"
FACEPP_API_SECRET = "vP8N1vVVa0G_4CfxXTyn2mIwwan9PXuL"
FACESET_TOKEN = None  # généré dynamiquement

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
GALA_FOLDER = "gala_photos"
OUTPUT_FOLDER = "generated"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GALA_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def facepp_detect(image_path):
    url = "https://api-us.faceplusplus.com/facepp/v3/detect"
    with open(image_path, "rb") as f:
        res = requests.post(url, data={
            "api_key": FACEPP_API_KEY,
            "api_secret": FACEPP_API_SECRET
        }, files={"image_file": f})
    return res.json()["faces"][0]["face_token"]

def facepp_compare(token1, token2):
    url = "https://api-us.faceplusplus.com/facepp/v3/compare"
    res = requests.post(url, data={
        "api_key": FACEPP_API_KEY,
        "api_secret": FACEPP_API_SECRET,
        "face_token1": token1,
        "face_token2": token2
    })
    return res.json().get("confidence", 0)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["selfie"]
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            selfie_token = facepp_detect(path)

            matched_photos = []
            for img in os.listdir(GALA_FOLDER):
                gala_path = os.path.join(GALA_FOLDER, img)
                try:
                    gala_token = facepp_detect(gala_path)
                    conf = facepp_compare(selfie_token, gala_token)
                    if conf > 75:
                        matched_photos.append(gala_path)
                except Exception:
                    continue

            user_folder = os.path.join(OUTPUT_FOLDER, selfie_token)
            os.makedirs(user_folder, exist_ok=True)
            for photo in matched_photos:
                copy2(photo, user_folder)

            return f"Photos copiées dans: {user_folder} — Tu peux créer un lien de partage depuis ce dossier."

    return render_template("index.html")
