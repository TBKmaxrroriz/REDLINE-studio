from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Mets ici ta clé et ton secret Face++
API_KEY = "zRpX_mvGViSiovfRh3-BdXsfKbTDkSyx"
API_SECRET = "vP8N1vVVa0G_4CfxXTyn2mIwwan9PXuL"

@app.route('/')
def index():
    return '''
    <h1>Upload une photo</h1>
    <form method="POST" action="/detect" enctype="multipart/form-data">
      <input type="file" name="photo" accept="image/*" required>
      <input type="submit" value="Envoyer">
    </form>
    '''

@app.route('/detect', methods=['POST'])
def detect_face():
    if 'photo' not in request.files:
        return jsonify({'error': 'Pas de fichier photo'}), 400
    
    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({'error': 'Fichier vide'}), 400

    # Sauvegarder temporairement l'image
    tmp_path = os.path.join('/tmp', photo.filename)
    photo.save(tmp_path)

    # Préparer la requête à Face++
    url = "https://api-us.faceplusplus.com/facepp/v3/detect"
    data = {
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'return_attributes': 'age,gender,smiling,emotion'
    }
    files = {'image_file': open(tmp_path, 'rb')}

    # Appeler Face++
    response = requests.post(url, data=data, files=files)
    os.remove(tmp_path)  # Supprimer le fichier temporaire
    
    if response.status_code != 200:
        return jsonify({'error': 'Erreur API Face++'}), 500

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
