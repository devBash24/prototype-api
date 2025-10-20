from flask import Blueprint
from routes.chat.controller import chat_with_ai

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint - accepts user questions and returns AI responses."""
    return chat_with_ai()
