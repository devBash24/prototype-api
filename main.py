from flask import Flask, jsonify
from routes.diagnose.route import diagnose_bp
from routes.chat.route import chat_bp
from routes.messages.route import messages_bp

app = Flask(__name__)

# Production configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
from flask_cors import CORS
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Plant Care API',
        'endpoints': {
            'diagnosis': '/plant/diagnose (POST) - Upload plant image for diagnosis',
            'chat': '/chat (POST) - Ask questions about plant care',
            'messages': '/messages (POST) - Chat with AI assistant with conversation management',
            'conversation': '/messages/conversation (GET) - Get conversation history',
            'conversations': '/messages/conversations (GET) - Get user conversations',
            'delete_conversation': '/messages/conversation (DELETE) - Delete conversation',
            'clear_all': '/messages/clear (DELETE) - Clear all conversations'
        },
        'status': 'active'
    })

# Register blueprints
app.register_blueprint(diagnose_bp, url_prefix='/plant')
app.register_blueprint(chat_bp, url_prefix='')
app.register_blueprint(messages_bp, url_prefix='')


if __name__ == '__main__':
    import os
    
    # Production configuration
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    ENV = os.environ.get('FLASK_ENV', 'development')
    
    if ENV == 'production':
        print(f"🌱 Plant Care API Starting in PRODUCTION mode...")
        print(f"🔧 Debug Mode: OFF")
        print(f"🌐 Host: {HOST}")
        print(f"📍 Port: {PORT}")
        print("-" * 50)
        
        # Production server configuration
        app.run(
            host=HOST,
            port=PORT,
            debug=False,
            threaded=True  # Enable threading for better performance
        )
    else:
        # Development configuration
        import socket
        
        def get_local_ip():
            """Get the local IP address of this machine."""
            try:
                # Connect to a remote server to determine local IP
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                return local_ip
            except Exception:
                return "127.0.0.1"  # Fallback to localhost
        
        # Get local IP for development
        local_ip = get_local_ip()
        
        print(f"🌱 Plant Care API Starting in DEVELOPMENT mode...")
        print(f"📍 Local Access: http://localhost:{PORT}")
        print(f"🌐 Network Access: http://{local_ip}:{PORT}")
        print(f"📱 Mobile/Other Devices: http://{local_ip}:{PORT}")
        print(f"🔧 Debug Mode: {'ON' if DEBUG else 'OFF'}")
        print("-" * 50)
        
        # Run the server
        app.run(
            host=HOST,  # Listen on all network interfaces
            port=PORT,
            debug=DEBUG
        )
