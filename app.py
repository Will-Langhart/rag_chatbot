from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from routes.chat import chat_bp
from routes.embeddings import embedding_bp

# Load environment variables
load_dotenv()

# Retrieve the LangChain API Key
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define the root route
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to the RAG Chatbot API",
        "endpoints": {
            "chat": "/api/chat",
            "embedding": "/api/embedding/embed"
        }
    })

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(embedding_bp, url_prefix='/api/embedding')

if __name__ == "__main__":
    app.run(debug=True)
