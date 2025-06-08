import os
import requests
import uuid
import shutil
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

# Clés Face++ (mets-les dans les variables d’environnement Render)
API_KEY = os.getenv('zRpX_mvGViSiovfRh3-BdXsfKbTDkSyx')
API_SECRET = os.getenv('vP8N1vVVa0G_4CfxXTyn2mIwwan9PXuL')

# Dossiers
UPLOAD_FOLDER = 'uploads'
PHOTOS_GALA = 'photos_gala'
PHOTOS_UTILISATEURS = 'photos_utilisateurs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PHOTOS_UTILISATEURS, exist_ok=True)

# Obtenir le face_token d'une image
def detect_face(image_path):
    response = requests.post(
        'https://api-us.faceplusplus.com/facepp/v3/detect',
        data={'api_key': API_KEY, 'api_secret': API_SECRET},
        files={'image_file': open(image_path, 'rb')}
    ).json()
    faces = response.get('faces', [])
    if faces:
        return faces[0]['face_token']
    return None

# Comparer deux visages
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
        uploaded_file = request.files['file']
        if not uploaded_file:
            return 'Aucun fichier reçu', 400

        selfie_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".jpg")
        uploaded_file.save(selfie_path)
        selfie_token = detect_face(selfie_path)
        if not selfie_token:
            return 'Aucun visage détecté', 400

        # Créer le dossier personnel
        user_id = str(uuid.uuid4())[:8]
        user_folder = os.path.join(PHOTOS_UTILISATEURS, user_id)
        os.makedirs(user_folder, exist_ok=True)

        # Parcourir les photos du gala
        for filename in os.listdir(PHOTOS_GALA):
            gala_path = os.path.join(PHOTOS_GALA, filename)
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            gala_token = detect_face(gala_path)
            if gala_token:
                confidence = compare_faces(selfie_token, gala_token)
                if confidence > 80:  # Seuil de similarité
                    shutil.copy(gala_path, os.path.join(user_folder, filename))

        return f'Ton dossier a été créé avec l\'identifiant : {user_id}'

    return render_template('upload.html')
