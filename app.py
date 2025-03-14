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
    if 'files[]' not in request.files:
        return "No files uploaded", 400
    
    files = request.files.getlist('files[]')  # Get multiple files

    if not files or all(f.filename == '' for f in files):
        return "No selected files", 400

    uploaded_files = []
    for file in files:
        if file.filename:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            uploaded_files.append(file.filename)

    # Git commit and push changes
    try:
        subprocess.run(["git", "add", "uploads"], check=True)
        subprocess.run(["git", "commit", "-m", f"Added {', '.join(uploaded_files)}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except subprocess.CalledProcessError as e:
        return f"Error updating GitHub: {str(e)}", 500

    return redirect(url_for('index'))

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
