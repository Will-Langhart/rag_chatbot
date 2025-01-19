from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # Relationships
    chats = db.relationship('Chat', backref='user', lazy=True)

    def __repr__(self):
        return f"<User id={self.id}, username={self.username}, email={self.email}>"

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def __repr__(self):
        return f"<Chat id={self.id}, user_id={self.user_id}, created_at={self.created_at}>"

class Embedding(db.Model):
    __tablename__ = 'embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    document = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.JSON, nullable=False)  # JSON to store vector embeddings
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    def __repr__(self):
        return f"<Embedding id={self.id}, created_at={self.created_at}>"
