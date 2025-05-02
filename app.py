from flask import Flask, request, render_template, send_from_directory, send_file
import os, uuid, qrcode
from datetime import datetime, timedelta
from io import BytesIO

app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def cleanup_old_files():
    now = datetime.now()
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            created = datetime.fromtimestamp(os.path.getctime(filepath))
            if now - created > timedelta(days=7):
                os.remove(filepath)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return 'Файл не выбран'
    
    uid = str(uuid.uuid4())
    filename = f"{uid}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    full_url = request.host_url.rstrip('/') + '/download/' + uid
    qr_url = '/generate_qr/' + uid

    return render_template('result.html', download_url=full_url, qr_url=qr_url)

@app.route('/download/<file_id>')
def download_file(file_id):
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        if f.startswith(file_id):
            return send_from_directory(app.config['UPLOAD_FOLDER'], f, as_attachment=True)
    return 'Файл не найден', 404

@app.route('/generate_qr/<file_id>')
def generate_qr(file_id):
    full_url = request.host_url.rstrip('/') + '/download/' + file_id
    img = qrcode.make(full_url)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
