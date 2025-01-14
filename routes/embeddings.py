from flask import Blueprint, request, jsonify, current_app
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

    current_app.logger.info(f"Received embedding request: document='{document}'")

    if not document:
        current_app.logger.warning("No document provided in the request.")
        return jsonify({"error": "Document is required"}), 400

    try:
        # Generate embeddings using OpenAI
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        vector = embeddings.embed_query(document)
        current_app.logger.info("Embeddings generated successfully.")

        # Store embeddings in Pinecone
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        index = Pinecone("rag-chatbot-index")
        index.upsert([(str(hash(document)), vector, {"document": document})])
        current_app.logger.info("Embeddings stored in Pinecone successfully.")

        # Save to PostgreSQL
        new_embedding = Embedding(document=document, embedding=vector)
        db.session.add(new_embedding)
        db.session.commit()
        current_app.logger.info("Embedding saved to database successfully.")

        return jsonify({"message": "Document embedded successfully"})

    except pinecone.exceptions.PineconeException as pe:
        current_app.logger.error(f"Pinecone error: {pe}")
        return jsonify({"error": f"Pinecone error: {str(pe)}"}), 500

    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
