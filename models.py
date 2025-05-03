"""
Database models for the Discord bot application.
"""
from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User model for authentication and bot ownership."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    servers = db.relationship('Server', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Server(db.Model):
    """Represents a Discord server the bot is connected to."""
    id = db.Column(db.Integer, primary_key=True)
    discord_server_id = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Bot settings for this server
    prefix = db.Column(db.String(10), default='!')
    ai_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='server', lazy=True)
    
    def __repr__(self):
        return f"<Server {self.name} ({self.discord_server_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'discord_server_id': self.discord_server_id,
            'name': self.name,
            'prefix': self.prefix,
            'ai_enabled': self.ai_enabled,
            'joined_at': self.joined_at.isoformat()
        }

class Conversation(db.Model):
    """Stores conversation history for AI context."""
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)
    channel_id = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation {self.id} in {self.channel_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'username': self.username,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat()
        }
