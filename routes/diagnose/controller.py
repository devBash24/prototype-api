import os
import tempfile
from flask import request, jsonify
from werkzeug.utils import secure_filename
from services.openai_client import OpenAIClient

# Initialize OpenAI client
openai_client = OpenAIClient()

# Allowed file extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def diagnose_plant():
    """
    Handle plant diagnosis requests with image upload.
    
    Expected request:
    - POST with multipart/form-data
    - 'image' field containing the plant image file
    - Optional 'additional_info' field with text context
    - Optional 'label' field with user-provided plant/crop name
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided. Please upload an image of your plant.'
            }), 400
        
        image_file = request.files['image']
        
        # Check if file is selected
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected. Please choose an image to upload.'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(image_file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get additional information and label if provided
        additional_info = request.form.get('additional_info', '')
        user_label = request.form.get('label', '')
        
        # Save uploaded file temporarily
        filename = secure_filename(image_file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        try:
            image_file.save(temp_path)
            
            # Perform diagnosis using OpenAI
            diagnosis_result = openai_client.diagnose_plant(temp_path, additional_info, user_label)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if diagnosis_result.get('success'):
                return jsonify({
                    'success': True,
                    'message': 'Plant diagnosis completed successfully',
                    'diagnosis': diagnosis_result['data'],
                    'model_used': openai_client.models['diagnosis']['vision_model'],
                    'additional_info': additional_info if additional_info else None,
                    'user_label': user_label if user_label else None
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': diagnosis_result.get('error', 'Diagnosis failed'),
                    'raw_response': diagnosis_result.get('raw_response')
                }), 500
                
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error during diagnosis: {str(e)}'
        }), 500
