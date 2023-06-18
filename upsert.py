from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from llama_index import SimpleDirectoryReader
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
import openai
import pinecone
import mimetypes
from utils.process import getCSV, getJSON, getWebsite
from langchain.document_loaders import PyPDFLoader


PINECONE_API_KEY = '2f1f9a16-8e97-4485-b643-bbcd3618570a'
PINECONE_ENVIRONMENT = 'us-west1-gcp-free'

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

index = pinecone.Index('wing-sandbox')
index.delete(delete_all=True)

openai_api_key = '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'
tokenizer = tiktoken.get_encoding('cl100k_base')

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQXNod2luIENoaXJ1bWFtaWxsYSJ9.keW___VBKcQY6uyxkxOH_uXZ1Jo74171cVa8SozxrKc"



UPSERT_BATCH_SIZE = 100

app = Flask(__name__)
CORS(app)


def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def process_csv(text):
    chunks = text_splitter.split_text(text)
    documents = []

    for i, chunk in enumerate(chunks):
        documents.append({
            'id': str(hash(chunk)),
            'text': chunk
        })

    return documents

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=['\n\n', '\n', ' ', '']
)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('data', filename)
    file.save(file_path)

    file_type, _ = mimetypes.guess_type(file_path)
    extension = file_type.split('/')[-1]

    if extension == 'pdf':
        predocs = load_document(file_path)
        print("File successfully loaded")
        documents = process_documents(predocs)
        post_documents = [{'id': doc['id'], 'text': doc['text']} for doc in documents]
        print("File successfully processed")
    
    elif extension == 'csv':
        text = getCSV(file_path)
        post_documents = process_csv(text)
        print("File successfully processed")
        

    for i in range(0, len(post_documents), UPSERT_BATCH_SIZE):
        i_end = min(i + UPSERT_BATCH_SIZE, len(post_documents))
        docs = post_documents[i:i_end]
        embeddings = get_embeddings([d['text'] for d in docs])
        vectors = [{'id': docs[n]['id'], 'values': embeddings[n], 'metadata': {}} for n in range(len(docs))]
        index.upsert(vectors=vectors)

    return filename + " upserted sucessfully"

@app.route('/query', methods=['POST'])
def query_chat():
    query = request.query_string
    query_embed = get_embeddings([query])[0]
    response = index.query(vector=query_embed, top_k=5)
    
    


def load_document(filename):
    loader = PyPDFLoader(filename)
    docs = loader.load()
    print(len(docs))
    return docs


def process_documents(docs):
    documents = []
    for doc in docs:
        chunks = text_splitter.split_text(doc.text)
        for i, chunk in enumerate(chunks):
            documents.append({
                'id': str(hash(chunk)),
                'text': chunk
            })

    return documents


def get_embeddings(texts):
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    data = response["data"]
    return [result["embedding"] for result in data]