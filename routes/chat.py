from flask import Blueprint, request, jsonify
from models import db, Chat
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.hub import pull
import os
import pinecone

# Load LangChain model using LangChainHub and API key
rephrase_model = pull("langchain-ai/chat-langchain-rephrase", api_key=os.getenv("LANGCHAIN_API_KEY"))

# Initialize Blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    # Extract JSON payload
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({"error": "User ID and message are required"}), 400

    try:
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        index = Pinecone("rag-chatbot-index")
        retriever = index.as_retriever()

        # Create the RAG chain with OpenAI LLM
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
        rag_chain = RetrievalQA(llm=llm, retriever=retriever)

        # Run the RAG chain to get the AI response
        raw_response = rag_chain.run(message)

        # Optionally rephrase the response using LangChainHub model
        rephrased_response = rephrase_model.run({"text": raw_response})

        # Save the chat to the database
        new_chat = Chat(user_id=user_id, message=message, response=rephrased_response)
        db.session.add(new_chat)
        db.session.commit()

        # Return the chatbot's response
        return jsonify({"response": rephrased_response})

    except pinecone.exceptions.PineconeException as pe:
        # Handle Pinecone-specific errors
        return jsonify({"error": f"Pinecone error: {str(pe)}"}), 500

    except Exception as e:
        # Handle general errors
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
