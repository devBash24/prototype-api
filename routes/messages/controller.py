from flask import request, jsonify
from services.openai_client import OpenAIClient
from datetime import datetime
import uuid

# Initialize OpenAI client
openai_client = OpenAIClient()

# In-memory conversation storage (in production, use a database)
conversations = {}

def send_message():
    """
    Handle chat messages with conversation management.
    
    Expected request:
    - POST with JSON data
    - 'message' field containing the user's message
    - Optional 'conversation_id' field to continue existing conversation
    - Optional 'user_id' field for user identification
    
    Returns:
    - AI response with conversation context
    - New conversation_id if starting new conversation
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided. Please send a message in JSON format.'
            }), 400
        
        # Extract user message
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'No message provided. Please include a message in your request.'
            }), 400
        
        # Get or create conversation ID
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id', 'anonymous')
        
        if not conversation_id:
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversations[conversation_id] = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'messages': []
            }
        
        # Check if conversation exists
        if conversation_id not in conversations:
            return jsonify({
                'success': False,
                'error': 'Conversation not found. Please start a new conversation.'
            }), 404
        
        # Get conversation history
        conversation = conversations[conversation_id]
        conversation_history = conversation['messages']
        
        # Update last activity
        conversation['last_activity'] = datetime.now().isoformat()
        
        # Chat with AI using RAG
        chat_result = openai_client.chat_with_ai(user_message, conversation_history)
        
        if chat_result.get('success'):
            # Add user message to conversation
            conversation['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Add AI response to conversation
            conversation['messages'].append({
                'role': 'assistant',
                'content': chat_result['response'],
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'message': 'Message sent successfully',
                'conversation_id': conversation_id,
                'response': chat_result['response'],
                'rag_context_used': chat_result.get('rag_context_used', False),
                'model_used': chat_result['model_used'],
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': chat_result.get('error', 'Chat failed'),
                'response': chat_result.get('response', 'Unable to generate response')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error during message processing: {str(e)}'
        }), 500

def get_conversation():
    """
    Get conversation history for a specific conversation ID.
    
    Expected request:
    - GET with 'conversation_id' query parameter
    
    Returns:
    - Full conversation history
    """
    try:
        conversation_id = request.args.get('conversation_id')
        
        if not conversation_id:
            return jsonify({
                'success': False,
                'error': 'conversation_id parameter is required'
            }), 400
        
        if conversation_id not in conversations:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        conversation = conversations[conversation_id]
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'user_id': conversation['user_id'],
            'created_at': conversation['created_at'],
            'last_activity': conversation['last_activity'],
            'message_count': len(conversation['messages']),
            'messages': conversation['messages']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error retrieving conversation: {str(e)}'
        }), 500

def get_user_conversations():
    """
    Get all conversations for a specific user.
    
    Expected request:
    - GET with 'user_id' query parameter
    
    Returns:
    - List of user's conversations
    """
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        user_conversations = []
        for conv_id, conv_data in conversations.items():
            if conv_data['user_id'] == user_id:
                user_conversations.append({
                    'conversation_id': conv_id,
                    'created_at': conv_data['created_at'],
                    'last_activity': conv_data['last_activity'],
                    'message_count': len(conv_data['messages']),
                    'last_message': conv_data['messages'][-1]['content'] if conv_data['messages'] else None
                })
        
        # Sort by last activity (most recent first)
        user_conversations.sort(key=lambda x: x['last_activity'], reverse=True)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'conversation_count': len(user_conversations),
            'conversations': user_conversations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error retrieving user conversations: {str(e)}'
        }), 500

def delete_conversation():
    """
    Delete a specific conversation.
    
    Expected request:
    - DELETE with 'conversation_id' query parameter
    
    Returns:
    - Confirmation of deletion
    """
    try:
        conversation_id = request.args.get('conversation_id')
        
        if not conversation_id:
            return jsonify({
                'success': False,
                'error': 'conversation_id parameter is required'
            }), 400
        
        if conversation_id not in conversations:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Delete conversation
        del conversations[conversation_id]
        
        return jsonify({
            'success': True,
            'message': 'Conversation deleted successfully',
            'conversation_id': conversation_id
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error deleting conversation: {str(e)}'
        }), 500

def clear_all_conversations():
    """
    Clear all conversations (admin function).
    
    Returns:
    - Confirmation of clearing all conversations
    """
    try:
        conversation_count = len(conversations)
        conversations.clear()
        
        return jsonify({
            'success': True,
            'message': f'All conversations cleared successfully',
            'deleted_count': conversation_count
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error clearing conversations: {str(e)}'
        }), 500
