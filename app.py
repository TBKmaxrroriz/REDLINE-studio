import os
import uuid
import shutil
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

# Clés Face++ en dur (pas sécurisé, à utiliser uniquement pour test rapide)
API_KEY = 'zRpX_mvGViSiovfRh3-BdXsfKbTDkSyx'
API_SECRET = 'vP8N1vVVa0G_4CfxXTyn2mIwwan9PXuL'

# Dossiers
UPLOAD_FOLDER = 'uploads'
PHOTOS_GALA = 'photos_gala'
PHOTOS_UTILISATEURS = 'photos_utilisateurs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PHOTOS_UTILISATEURS, exist_ok=True)

def detect_face(image_path):
    with open(image_path, 'rb') as img_file:
        response = requests.post(
            'https://api-us.faceplusplus.com/facepp/v3/detect',
            data={'api_key': API_KEY, 'api_secret': API_SECRET},
            files={'image_file': img_file}
        ).json()
    faces = response.get('faces', [])
    if faces:
        return faces[0]['face_token']
    return None

def compare_faces(token1, token2):
    response = requests.post(
        'https://api-us.faceplusplus.com/facepp/v3/compare',
        data={
            'api_key': API_KEY,
            'api_secret': API_SECRET,
            'face_token1': token1,
            'face_token2': token2
        }
    ).json()
    return response.get('confidence', 0)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Aucun fichier reçu', 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return 'Aucun fichier sélectionné', 400

        selfie_filename = f"{uuid.uuid4()}.jpg"
        selfie_path = os.path.join(UPLOAD_FOLDER, selfie_filename)
        uploaded_file.save(selfie_path)

        selfie_token = detect_face(selfie_path)
        if not selfie_token:
            os.remove(selfie_path)
            return 'Aucun visage détecté sur la photo selfie.', 400

        user_id = str(uuid.uuid4())[:8]
        user_folder = os.path.join(PHOTOS_UTILISATEURS, user_id)
        os.makedirs(user_folder, exist_ok=True)

        copied_photos = 0
        for filename in os.listdir(PHOTOS_GALA):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            gala_path = os.path.join(PHOTOS_GALA, filename)
            gala_token = detect_face(gala_path)
            if gala_token:
                confidence = compare_faces(selfie_token, gala_token)
                if confidence > 80:
                    shutil.copy(gala_path, os.path.join(user_folder, filename))
                    copied_photos += 1

        os.remove(selfie_path)

        if copied_photos == 0:
            return f"Aucune photo correspondante trouvée pour ce visage. ID: {user_id}"

        return f"Dossier créé avec {copied_photos} photo(s). Ton identifiant est : {user_id}"

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
