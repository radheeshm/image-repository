from flask import Flask, request, send_from_directory, render_template, redirect, url_for
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    images = os.listdir(UPLOAD_FOLDER)
    image_urls = [f'/images/{img}' for img in images]
    return render_template('index.html', images=image_urls)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Save the uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Git commit and push
    try:
        subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)
        subprocess.run(["git", "add", "uploads"], check=True)
        subprocess.run(["git", "commit", "-m", f"Added {file.filename}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except subprocess.CalledProcessError as e:
        return f"Error updating GitHub: {str(e)}", 500

    return redirect(url_for('index'))

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
