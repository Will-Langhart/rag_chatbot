from flask import Blueprint, request, jsonify, current_app
from models import db, Chat
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from pinecone import Pinecone, ServerlessSpec
import os
import logging

# Set up a standalone logger for initialization outside the Flask app context
module_logger = logging.getLogger("chat_module")
module_logger.setLevel(logging.DEBUG)

# Initialize Blueprint
chat_bp = Blueprint('chat', __name__)

# Create and initialize a Pinecone client
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    module_logger.info("Pinecone client initialized successfully.")
except Exception as e:
    pc = None
    module_logger.error(f"Failed to initialize Pinecone client: {e}")

@chat_bp.route('/', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')

    current_app.logger.info(f"Received chat request: user_id={user_id}, message='{message}'")

    if not user_id or not message:
        current_app.logger.warning("Missing user_id or message in request.")
        return jsonify({"error": "User ID and message are required"}), 400

    try:
        # Ensure Pinecone client is initialized
        if not pc:
            raise ValueError("Pinecone client is not initialized. Check API key and configuration.")

        # Use a fixed index name
        index_name = "rag-chatbot-index-final"

        # List existing indexes
        existing_indexes = [index["name"] for index in pc.list_indexes()]
        current_app.logger.debug(f"Existing Pinecone indexes: {existing_indexes}")

        # Create index if it doesn't exist
        if index_name not in existing_indexes:
            current_app.logger.info(f"Creating Pinecone index '{index_name}'.")
            pc.create_index(
                name=index_name,
                dimension=1536,  # Adjust based on your embedding size
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",  # AWS setup
                    region=os.getenv("PINECONE_REGION", "us-east-1")
                ),
            )
            current_app.logger.info(f"Pinecone index '{index_name}' created.")
        else:
            current_app.logger.info(f"Pinecone index '{index_name}' already exists.")

        # Access the index using the Pinecone client
        index = pc.Index(index_name)
        current_app.logger.info(f"Pinecone index '{index_name}' accessed successfully.")

        # Initialize OpenAI embeddings
        embedding = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        current_app.logger.info("OpenAI Embeddings initialized successfully.")

        # Simulate RetrievalQA and OpenAI response
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
        raw_response = f"Simulated response for message: '{message}'"
        current_app.logger.info(f"Raw response: {raw_response}")

        # Save the chat to the database within app context
        with current_app.app_context():
            new_chat = Chat(user_id=user_id, message=message, response=raw_response)
            db.session.add(new_chat)
            db.session.commit()
            current_app.logger.info("Chat saved to database successfully.")

        return jsonify({"response": raw_response})

    except ValueError as ve:
        current_app.logger.error(f"Configuration error: {ve}")
        return jsonify({"error": f"Configuration error: {str(ve)}"}), 500

    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
