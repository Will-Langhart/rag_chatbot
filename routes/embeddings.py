from flask import Blueprint, request, jsonify
from models import db, Embedding
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
import os

# Initialize Blueprint
embedding_bp = Blueprint('embedding', __name__)

@embedding_bp.route('/embed', methods=['POST'])
def embed_document():
    data = request.json
    document = data.get('document')

    if not document:
        return jsonify({"error": "Document is required"}), 400

    try:
        # Generate embeddings using OpenAI
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        vector = embeddings.embed_query(document)

        # Store embeddings in Pinecone
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        index = pinecone.Index("rag-chatbot-index")
        index.upsert([(str(hash(document)), vector, {"document": document})])

        # Save to PostgreSQL
        new_embedding = Embedding(document=document, embedding=vector)
        db.session.add(new_embedding)
        db.session.commit()

        return jsonify({"message": "Document embedded successfully"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
