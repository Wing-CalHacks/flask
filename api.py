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
PINECONE_API_KEY = '2f1f9a16-8e97-4485-b643-bbcd3618570a'
PINECONE_ENVIRONMENT='us-west1-gcp-free'
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pinecone.Index('wing-sandbox')

openai_api_key = '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'
tokenizer = tiktoken.get_encoding('cl100k_base')
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQXNod2luIENoaXJ1bWFtaWxsYSJ9.keW___VBKcQY6uyxkxOH_uXZ1Jo74171cVa8SozxrKc"

def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,  # number of tokens overlap between chunks
    length_function=tiktoken_len,
    separators=['\n\n', '\n', ' ', '']
)

app = Flask(__name__)
CORS(app)
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join('data', filename)
    file.save(file_path)
    predocs = load_document()
    print("File successfully loaded")
    print(len(predocs))
    documents = process_documents(predocs)
    print(len(documents))
    post_documents = [{
    'id': doc['id'],
    'text': doc['text'],
    'metadata': {'url': doc['source']}
    } for doc in documents]     
    print("File sucessfully processed")
    UPSERT_BATCH_SIZE = 100
    for i in range(0, len(post_documents), UPSERT_BATCH_SIZE):
        i_end = min(i + UPSERT_BATCH_SIZE, len(post_documents))
        docs = post_documents[i:i_end]
        embeddings = get_embeddings([d['text'] for d in docs])
        vectors = [{
            'id': docs[n]['id'],
            'values': embeddings[n],
            'metadata': {}
        } for n in range(len(docs))]
        index.upsert(vectors=vectors)
    return "File sucessfully upserted"
    
    


def load_document():
    loader = SimpleDirectoryReader('data', recursive=True, exclude_hidden=True)
    docs = loader.load_data()
    print(len(docs))
    return docs

def process_documents(docs):
    m = hashlib.md5()
    documents = []

    for doc in docs:
        url = doc.doc_id
        source = url
        m.update(url.encode('utf-8'))
        uid = m.hexdigest()[:12]
        chunks = text_splitter.split_text(doc.text)
        for i, chunk in enumerate(chunks):
            documents.append({
                'id': f'{uid}-{i}',
                'text': chunk,
                'source': source
            })
    
    return documents

def get_embeddings(texts):
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    data = response["data"]
    return [result["embedding"] for result in data]