from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from routes.chat import chat_bp
from routes.embeddings import embedding_bp
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(embedding_bp, url_prefix='/api/embedding')

if __name__ == "__main__":
    app.run(debug=True)
