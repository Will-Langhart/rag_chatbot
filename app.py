from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from app import db
import logging
from logging.handlers import RotatingFileHandler
from routes.chat import chat_bp
from routes.embeddings import embedding_bp

# Load environment variables
load_dotenv()

# Retrieve the LangChain API Key
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler("error.log", maxBytes=100000, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Define the root route
@app.route('/')
def index():
    return render_template('index.html')

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(embedding_bp, url_prefix='/api/embedding')

# Error handler for 404 errors
@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 Error: {error}")
    return jsonify({"error": "This resource was not found"}), 404

# Error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 Error: {error}")
    return jsonify({"error": "An internal server error occurred"}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
