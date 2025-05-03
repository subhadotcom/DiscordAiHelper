"""
Flask application for the Discord bot dashboard.
Provides a web interface for managing bot settings and viewing statistics.
"""
import os
import logging

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Setup the base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize Flask application and SQLAlchemy
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import models after db initialization to avoid circular imports
with app.app_context():
    from models import User, Server, Conversation
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page for authenticated users."""
    servers = Server.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', servers=servers)

@app.route('/api/servers', methods=['GET'])
@login_required
def get_servers():
    """API endpoint to get the user's servers."""
    servers = Server.query.filter_by(user_id=current_user.id).all()
    return jsonify([server.to_dict() for server in servers])

@app.route('/api/conversations/<server_id>', methods=['GET'])
@login_required
def get_conversations(server_id):
    """API endpoint to get conversations for a server."""
    server = Server.query.filter_by(id=server_id, user_id=current_user.id).first()
    if not server:
        return jsonify({"error": "Server not found"}), 404
    
    conversations = Conversation.query.filter_by(server_id=server_id).all()
    return jsonify([conv.to_dict() for conv in conversations])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {e}")
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
