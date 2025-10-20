from flask import request, jsonify
from services.openai_client import OpenAIClient

# Initialize OpenAI client
openai_client = OpenAIClient()

def chat_with_ai():
    """
    Handle chat requests with users about plant care.
    
    Expected request:
    - POST with JSON data
    - 'message' field containing the user's question
    - Optional 'conversation_history' field with previous messages
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        print(data)
        
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
        
        # Get conversation history if provided
        conversation_history = data.get('conversation_history', [])
        
        # Validate conversation history format
        if conversation_history and not isinstance(conversation_history, list):
            return jsonify({
                'success': False,
                'error': 'Conversation history must be a list of message objects.'
            }), 400
        
        # Chat with AI
        chat_result = openai_client.chat_with_ai(user_message, conversation_history)
        
        if chat_result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Chat response generated successfully',
                'response': chat_result['response'],
                'conversation_history': chat_result['conversation_history'],
                'model_used': chat_result['model_used']
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
            'error': f'Server error during chat: {str(e)}'
        }), 500
