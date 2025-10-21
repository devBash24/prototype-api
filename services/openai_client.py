import os
import base64
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClient:
    def __init__(self):
        """Initialize OpenAI client with API key from environment variables."""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Model configurations for different use cases
        self.models = {
            'diagnosis': {
                'vision_model': 'gpt-4o-mini',  # Most affordable vision model
                'fallback_model': 'gpt-3.5-turbo'  # Fallback for text-only
            },
            'chat': {
                'primary_model': 'gpt-3.5-turbo',  # Most affordable for chat
                'fallback_model': 'gpt-4o-mini'  # Fallback if needed
            }
        }
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64 string for OpenAI API."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error encoding image: {str(e)}")
    
    def diagnose_plant(self, image_path: str, additional_info: Optional[str] = None, user_label: Optional[str] = None) -> Dict[str, Any]:
        """
        Diagnose plant health from image using OpenAI vision model.
        
        Args:
            image_path: Path to the plant image
            additional_info: Optional additional context about the plant
            user_label: Optional user-provided plant/crop label
            
        Returns:
            Dictionary containing plant name, status, confidence, cause, treatment, and prevention
        """
        try:
            # Encode image to base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # Prepare the prompt for plant diagnosis
            prompt = self._get_diagnosis_prompt(additional_info, user_label)
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.models['diagnosis']['vision_model'],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent medical advice
            )
            
            # Parse and structure the response
            diagnosis_text = response.choices[0].message.content
            return self._parse_diagnosis_response(diagnosis_text)
            
        except Exception as e:
            # Fallback to text-only model if vision model fails
            return self._fallback_diagnosis(str(e), additional_info, user_label)
    
    def chat_with_ai(self, user_message: str, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Handle chat conversations with users about plants.
        
        Args:
            user_message: User's question or message
            conversation_history: Optional list of previous messages
            
        Returns:
            Dictionary containing AI response and updated conversation history
        """
        try:
            # Prepare messages for chat
            messages = self._prepare_chat_messages(user_message, conversation_history)
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.models['chat']['primary_model'],
                messages=messages,
                max_tokens=500,
                temperature=0.7  # Higher temperature for more conversational responses
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            updated_history = self._update_conversation_history(
                conversation_history or [], user_message, ai_response
            )
            
            return {
                'success': True,
                'response': ai_response,
                'conversation_history': updated_history,
                'model_used': self.models['chat']['primary_model']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Chat error: {str(e)}",
                'response': "I'm sorry, I'm having trouble responding right now. Please try again later."
            }
    
    def _get_diagnosis_prompt(self, additional_info: Optional[str] = None, user_label: Optional[str] = None) -> str:
        """Generate the prompt for plant diagnosis."""
        base_prompt = """
        You are a friendly plant health expert. Look carefully at this plant image and give a clear, easy-to-understand diagnosis.

IMPORTANT: Reply with ONLY a valid JSON object in this exact format:
{
    "name": "Common name of the plant or crop (e.g., 'Tomato', 'Rose', 'Unknown')",
    "status": "healthy|unhealthy|diseased|pest_infested|nutrient_deficient|stressed",
    "confidence": 85,
    "problem": "Describe what you actually see happening (e.g., 'Leaves turning yellow at the bottom', 'Brown spots spreading on leaves', 'Wilting stems', 'Looks healthy overall')",
    "cause": "Explain in simple terms what’s causing it (e.g., 'Fungal infection', 'Insect damage', 'Lack of nutrients', 'Too much water', 'Normal growth')",
    "treatment": "Give easy-to-follow steps to help the plant recover (e.g., 'Remove affected leaves and spray with a mild fungicide')",
    "prevention": "Practical tips to stop it from happening again (e.g., 'Water early in the morning and avoid wetting leaves')"
}

Guidelines:
1. Identify the plant or crop name if possible; use "Unknown" if unsure.
2. Judge how the plant looks — healthy, unhealthy, or showing disease, pest, or nutrient problems.
3. Set confidence as a percentage (0–100) based on how sure you are.
4. Describe the visible issue in plain language.
5. Keep explanations short, clear, and easy to understand.
6. Give practical treatment steps anyone can follow at home.
7. Suggest simple prevention tips to keep the plant healthy.
8. Don’t assume every plant is healthy — be honest about what you see.

Focus on:
- Simple, friendly language anyone can understand.
- Useful, realistic advice for home gardeners.
- Clear separation between what’s happening, why, and what to do.

        """
        
        if user_label:
            base_prompt += f"\n\nUser-provided plant label: {user_label}"
        
        if additional_info:
            base_prompt += f"\n\nAdditional context provided by user: {additional_info}"
        
        base_prompt += "\n\nRespond with ONLY the JSON object, no additional text."
        
        return base_prompt
    
    def _parse_diagnosis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the diagnosis response from OpenAI."""
        try:
            import json
            import re
            
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Try to parse as direct JSON first
            try:
                diagnosis_data = json.loads(cleaned_text)
                # Validate required fields
                required_fields = ['name', 'status', 'confidence', 'problem', 'cause', 'treatment', 'prevention']
                if all(field in diagnosis_data for field in required_fields):
                    # Validate confidence is a number
                    if isinstance(diagnosis_data.get('confidence'), (int, float)):
                        return {
                            'success': True,
                            'data': diagnosis_data,
                            'raw_response': response_text
                        }
            except json.JSONDecodeError:
                pass
            
            # Look for JSON in the response using regex
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    diagnosis_data = json.loads(json_match.group())
                    # Validate required fields
                    required_fields = ['name', 'status', 'confidence', 'problem', 'cause', 'treatment', 'prevention']
                    if all(field in diagnosis_data for field in required_fields):
                        # Validate confidence is a number
                        if isinstance(diagnosis_data.get('confidence'), (int, float)):
                            return {
                                'success': True,
                                'data': diagnosis_data,
                                'raw_response': response_text
                            }
                except json.JSONDecodeError:
                    pass
            
            # If no valid JSON found, create a structured response
            return {
                'success': True,
                'data': {
                    'name': 'Unknown',
                    'status': 'unknown',
                    'confidence': 25,
                    'problem': 'Unable to analyze image properly',
                    'cause': 'Unable to parse AI response properly',
                    'treatment': 'Please try uploading a clearer image or consult a plant expert',
                    'prevention': 'Ensure good plant care practices and regular monitoring'
                },
                'raw_response': response_text,
                'parsing_warning': 'Response was not in expected JSON format'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error parsing diagnosis response: {str(e)}",
                'raw_response': response_text
            }
    
    def _fallback_diagnosis(self, error_message: str, additional_info: Optional[str] = None, user_label: Optional[str] = None) -> Dict[str, Any]:
        """Fallback diagnosis using text-only model when vision model fails."""
        try:
            prompt = f"""
            I encountered an error with the image analysis: {error_message}
            
            Please provide a response in the following JSON format:
            {{
                "name": "{user_label or 'Unknown'}",
                "status": "unknown",
                "confidence": 15,
                "problem": "Unable to analyze image due to technical issues",
                "cause": "Image analysis failed - {error_message}",
                "treatment": "Please try uploading a clearer image or consult a plant expert",
                "prevention": "Ensure good plant care practices and regular monitoring"
            }}
            
            Based on the additional information provided: {additional_info or 'No additional information'}
            """
            
            response = self.client.chat.completions.create(
                model=self.models['diagnosis']['fallback_model'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            fallback_response = response.choices[0].message.content
            try:
                import json
                fallback_data = json.loads(fallback_response)
                return {
                    'success': True,
                    'data': fallback_data,
                    'fallback_used': True,
                    'error': error_message
                }
            except:
                return {
                    'success': True,
                    'data': {
                        'name': user_label or 'Unknown',
                        'status': 'unknown',
                        'confidence': 15,
                        'problem': 'Unable to analyze image due to technical issues',
                        'cause': f'Image analysis failed - {error_message}',
                        'treatment': 'Please try uploading a clearer image or consult a plant expert',
                        'prevention': 'Ensure good plant care practices and regular monitoring'
                    },
                    'fallback_used': True,
                    'error': error_message
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"Fallback diagnosis failed: {str(e)}"
            }
    
    def _prepare_chat_messages(self, user_message: str, conversation_history: Optional[list] = None) -> list:
        """Prepare messages for chat API call."""
        messages = [
            {
                "role": "system",
                "content": """You are a helpful plant care assistant. You can answer questions about:
                - Plant identification
                - Plant care and maintenance
                - Common plant problems and solutions
                - Growing tips and advice
                - Plant diseases and pests
                
                Be friendly, informative, and practical in your responses. If you're unsure about something, 
                recommend consulting with a local plant expert or nursery."""
            }
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _update_conversation_history(self, history: list, user_message: str, ai_response: str) -> list:
        """Update conversation history with new messages."""
        # Keep only last 10 messages to manage token usage
        max_history = 10
        
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": ai_response})
        
        # Trim history if too long
        if len(history) > max_history:
            history = history[-max_history:]
        
        return history
