from flask import Blueprint, request, jsonify, current_app
from models import db, Chat, User
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone as LangChainPinecone
from sqlalchemy.sql import text
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
        # Verify database connection
        db.session.execute(text("SELECT 1"))
        current_app.logger.info("Database connection verified.")

        # Ensure Pinecone client is initialized
        if not pc:
            raise ValueError("Pinecone client is not initialized. Check API key and configuration.")

        # Ensure user exists
        user = User.query.get(user_id)
        if not user:
            current_app.logger.warning(f"Invalid user ID: {user_id}")
            return jsonify({"error": "Invalid user ID."}), 400

        # Use a fixed index name
        index_name = "rag-chatbot-index-final"

        # Check if the index exists using the Pinecone client
        try:
            index_info = pc.describe_index(index_name)
            current_app.logger.info(f"Pinecone index '{index_name}' exists and is ready.")
        except Exception as e:
            current_app.logger.info(f"Pinecone index '{index_name}' does not exist. Creating it.")
            pc.create_index(
                name=index_name,
                dimension=1536,  # Adjust based on your embedding size
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",  # AWS setup
                    region=os.getenv("PINECONE_REGION", "us-east-1")
                ),
            )
            current_app.logger.info(f"Pinecone index '{index_name}' created successfully.")

        # Access the index using LangChain's Pinecone integration
        retriever = LangChainPinecone.from_existing_index(
            index_name=index_name,
            embedding=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        )
        current_app.logger.info(f"Pinecone index '{index_name}' accessed successfully.")

        # Create RetrievalQA with OpenAI LLM
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
        rag_chain = RetrievalQA(llm=llm, retriever=retriever)
        response = rag_chain.run(message)
        current_app.logger.info(f"Generated response: {response}")

        # Save the chat to the database
        new_chat = Chat(user_id=user_id, message=message, response=response)
        db.session.add(new_chat)
        db.session.commit()
        current_app.logger.info("Chat saved to database successfully.")

        return jsonify({"response": response})

    except ValueError as ve:
        current_app.logger.error(f"Configuration error: {ve}")
        return jsonify({"error": f"Configuration error: {str(ve)}"}), 500

    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
