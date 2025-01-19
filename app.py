from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from models import db
from routes.chat import chat_bp
from routes.embeddings import embedding_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler("error.log", maxBytes=100000, backupCount=3)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Verify database connectivity on startup
@app.before_first_request
def verify_database_connection():
    try:
        with app.app_context():
            db.session.execute("SELECT 1")  # Simple query to verify connection
            app.logger.info("Database connection established successfully.")
    except Exception as e:
        app.logger.critical(f"Database connection failed: {e}")

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
    app.logger.error(f"500 Error: {error}", exc_info=True)
    return jsonify({"error": "An internal server error occurred"}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
