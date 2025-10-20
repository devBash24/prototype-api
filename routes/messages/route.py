from flask import Blueprint
from routes.messages.controller import (
    send_message,
    get_conversation,
    get_user_conversations,
    delete_conversation,
    clear_all_conversations
)

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages', methods=['POST'])
def send_message_endpoint():
    """
    Send a message to the AI assistant.
    
    Request body:
    {
        "message": "Your message here",
        "conversation_id": "optional-existing-conversation-id",
        "user_id": "optional-user-identifier"
    }
    
    Response:
    {
        "success": true,
        "conversation_id": "conversation-uuid",
        "response": "AI response",
        "rag_context_used": true,
        "model_used": "gpt-3.5-turbo",
        "timestamp": "2024-01-01T12:00:00"
    }
    """
    return send_message()

@messages_bp.route('/messages/conversation', methods=['GET'])
def get_conversation_endpoint():
    """
    Get conversation history for a specific conversation.
    
    Query parameters:
    - conversation_id: The conversation ID to retrieve
    
    Response:
    {
        "success": true,
        "conversation_id": "conversation-uuid",
        "user_id": "user-identifier",
        "created_at": "2024-01-01T12:00:00",
        "last_activity": "2024-01-01T12:30:00",
        "message_count": 10,
        "messages": [...]
    }
    """
    return get_conversation()

@messages_bp.route('/messages/conversations', methods=['GET'])
def get_user_conversations_endpoint():
    """
    Get all conversations for a specific user.
    
    Query parameters:
    - user_id: The user ID to get conversations for (defaults to 'anonymous')
    
    Response:
    {
        "success": true,
        "user_id": "user-identifier",
        "conversation_count": 5,
        "conversations": [...]
    }
    """
    return get_user_conversations()

@messages_bp.route('/messages/conversation', methods=['DELETE'])
def delete_conversation_endpoint():
    """
    Delete a specific conversation.
    
    Query parameters:
    - conversation_id: The conversation ID to delete
    
    Response:
    {
        "success": true,
        "message": "Conversation deleted successfully",
        "conversation_id": "conversation-uuid"
    }
    """
    return delete_conversation()

@messages_bp.route('/messages/clear', methods=['DELETE'])
def clear_all_conversations_endpoint():
    """
    Clear all conversations (admin function).
    
    Response:
    {
        "success": true,
        "message": "All conversations cleared successfully",
        "deleted_count": 25
    }
    """
    return clear_all_conversations()
