from flask import Flask, request
from llama_index import download_loader, SimpleDirectoryReader


app = Flask(__name__)

@app.route("/")
def upload_file():
    file = request.files['file']
    loader = SimpleDirectoryReader('./data', recursive=True, exclude_hidden=True)
    documents = loader.load_data()
    return documents
