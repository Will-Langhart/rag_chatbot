from flask import Flask
from config import Config
from models import db
from routes.chat import chat_bp
from routes.embeddings import embedding_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(embedding_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)
