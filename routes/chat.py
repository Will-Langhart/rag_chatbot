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
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({"error": "User ID and message are required"}), 400

    try:
        # Retrieve relevant context from Pinecone
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        index = Pinecone("rag-chatbot-index")
        retriever = index.as_retriever()

        # Create the RAG chain
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
        rag_chain = RetrievalQA(llm=llm, retriever=retriever)
        response = rag_chain.run(message)

        # Use the rephrase model from LangChainHub
        rephrased_response = rephrase_model.run({"text": response})

        # Save chat to PostgreSQL
        new_chat = Chat(user_id=user_id, message=message, response=rephrased_response)
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({"response": rephrased_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
