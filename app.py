from flask import Flask, request, render_template
import os

app = Flask(__name__)
UPLOAD_FOLDER = "selfies"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['selfie']
    name = request.form['fullname'].strip().replace(" ", "_").lower()
    if file and name:
        filename = f"{name}.jpg"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return f"Merci {name.title()} ! Ton selfie a bien été reçu 🙌"
    return "Erreur : vérifie que tout est rempli."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)