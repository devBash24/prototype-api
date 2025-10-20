from flask import Flask, jsonify
from routes.diagnose.route import diagnose_bp
from routes.chat.route import chat_bp

app = Flask(__name__)

# Enable CORS for all routes
from flask_cors import CORS
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Plant Care API',
        'endpoints': {
            'diagnosis': '/plant/diagnose (POST) - Upload plant image for diagnosis',
            'chat': '/chat (POST) - Ask questions about plant care'
        },
        'status': 'active'
    })

# Register blueprints
app.register_blueprint(diagnose_bp, url_prefix='/plant')
app.register_blueprint(chat_bp, url_prefix='')


if __name__ == '__main__':
    # Get your local IP address automatically
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
    
    # Get local IP and port
    HOST = get_local_ip()
    PORT = 5000
    
    print(f"🌱 Plant Care API Starting...")
    print(f"📍 Local Access: http://localhost:{PORT}")
    print(f"🌐 Network Access: http://{HOST}:{PORT}")
    print(f"📱 Mobile/Other Devices: http://{HOST}:{PORT}")
    print(f"🔧 Debug Mode: {'ON' if True else 'OFF'}")
    print("-" * 50)
    
    # Run the server
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=PORT,
        debug=True
    )
