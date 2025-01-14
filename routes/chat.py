from flask import Blueprint, request, jsonify, current_app
from models import db, Chat
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.hub import pull
import os
import pinecone
import logging

# Set up a standalone logger for initialization outside the Flask app context
module_logger = logging.getLogger("chat_module")
module_logger.setLevel(logging.DEBUG)

try:
    rephrase_model = pull("langchain-ai/chat-langchain-rephrase", api_key=os.getenv("LANGCHAIN_API_KEY"))
    module_logger.info("LangChain rephrase model loaded successfully.")
except Exception as e:
    rephrase_model = None
    module_logger.error(f"Failed to load LangChain rephrase model: {e}")

# Initialize Blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')

    current_app.logger.info(f"Received chat request: user_id={user_id}, message='{message}'")

    if not user_id or not message:
        current_app.logger.warning("Missing user_id or message in request.")
        return jsonify({"error": "User ID and message are required"}), 400

    try:
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        index = Pinecone("rag-chatbot-index")
        retriever = index.as_retriever()
        current_app.logger.info("Pinecone initialized and retriever set up.")

        # Create the RAG chain with OpenAI LLM
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
        rag_chain = RetrievalQA(llm=llm, retriever=retriever)
        current_app.logger.info("RetrievalQA chain created successfully.")

        # Run the RAG chain to get the AI response
        raw_response = rag_chain.run(message)
        current_app.logger.info(f"Raw response from RAG chain: {raw_response}")

        # Optionally rephrase the response using LangChainHub model
        rephrased_response = rephrase_model.run({"text": raw_response}) if rephrase_model else raw_response

        # Save the chat to the database
        new_chat = Chat(user_id=user_id, message=message, response=rephrased_response)
        db.session.add(new_chat)
        db.session.commit()
        current_app.logger.info("Chat saved to database successfully.")

        return jsonify({"response": rephrased_response})

    except pinecone.exceptions.PineconeException as pe:
        current_app.logger.error(f"Pinecone error: {pe}")
        return jsonify({"error": f"Pinecone error: {str(pe)}"}), 500

    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
