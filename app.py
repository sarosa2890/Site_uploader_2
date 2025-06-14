from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import qrcode
import uuid

app = Flask(__name__)

# Папка для сохранения файлов
UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'static/qr'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Убедись, что папки существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # Показывает форму загрузки

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Имя файла пустое'}), 400

    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    saved_filename = f"{file_id}_{filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
    file.save(save_path)

    # Генерация ссылки для скачивания
    download_url = url_for('download_file', filename=saved_filename, _external=True)

    # Генерация QR-кода
    qr_img = qrcode.make(download_url)
    qr_filename = f"{file_id}.png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)
    qr_img.save(qr_path)

    # Вернуть JSON с редиректом на страницу успешной загрузки
    return jsonify({'redirect_url': url_for('uploaded', file_id=file_id, filename=saved_filename)})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/uploaded')
def uploaded():
    filename = request.args.get('filename')
    file_id = request.args.get('file_id')
    download_url = url_for('download_file', filename=filename, _external=True)
    qr_url = url_for('static', filename=f'qr/{file_id}.png')

    return render_template('result.html', download_url=download_url, qr_url=qr_url)

if __name__ == '__main__':
    app.run(debug=True)
