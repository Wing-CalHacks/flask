from flask import Flask, request, send_file
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)


@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('data', filename)
    file.save(file_path)
    return send_file(file_path, as_attachment=True)
