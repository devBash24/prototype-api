# Plant Care API

A Flask-based API that uses OpenAI's models to provide plant diagnosis and chat functionality.

## Features

- **Plant Diagnosis**: Upload plant images for AI-powered health diagnosis
- **Chat Support**: Ask questions about plant care and get AI responses
- **Cost-Effective**: Uses the most affordable OpenAI models for each use case
- **Multiple Model Support**: Automatic fallback between models for reliability

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Plant Diagnosis - `/plant/diagnose` (POST)

Upload a plant image for AI-powered diagnosis.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Fields:
  - `image` (required): Plant image file (PNG, JPG, JPEG, GIF, BMP, WEBP)
  - `additional_info` (optional): Additional context about the plant
  - `label` (optional): User-provided plant/crop name

**Response:**
```json
{
  "success": true,
  "message": "Plant diagnosis completed successfully",
  "diagnosis": {
    "name": "Tomato",
    "status": "nutrient_deficient",
    "confidence": 85,
    "problem": "Yellowing leaves on lower branches with brown edges",
    "cause": "Nitrogen deficiency due to poor soil nutrition",
    "treatment": "Apply balanced fertilizer every 2 weeks and ensure proper watering",
    "prevention": "Maintain consistent watering schedule and soil pH between 6.0-6.8"
  },
  "model_used": "gpt-4o-mini",
  "additional_info": "User provided context",
  "user_label": "Tomato Plant"
}
```

### 2. Chat - `/chat` (POST)

Ask questions about plant care and get AI responses.

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
```json
{
  "message": "How often should I water my succulents?",
  "conversation_history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat response generated successfully",
  "response": "AI response to your question",
  "conversation_history": [
    {"role": "user", "content": "Your question"},
    {"role": "assistant", "content": "AI response"}
  ],
  "model_used": "gpt-3.5-turbo"
}
```

## Model Configuration

The API uses different OpenAI models optimized for cost and performance:

- **Diagnosis**: `gpt-4o-mini` (most affordable vision model)
- **Chat**: `gpt-3.5-turbo` (most affordable for conversations)

Fallback models are automatically used if the primary models fail.

## Status Values

The diagnosis endpoint returns health status with these possible values:
- `healthy`: Plant appears to be in good condition
- `unhealthy`: Plant shows signs of poor health
- `diseased`: Plant has visible disease symptoms
- `pest_infested`: Plant is affected by pests
- `nutrient_deficient`: Plant shows nutrient deficiency signs
- `stressed`: Plant is under stress (environmental, water, etc.)
- `unknown`: Unable to determine health status

## Error Handling

The API includes comprehensive error handling for:
- Invalid file types
- Missing API keys
- OpenAI API errors
- File upload issues
- Malformed requests

## Example Usage

### Using curl for diagnosis:
```bash
curl -X POST http://localhost:5000/plant/diagnose \
  -F "image=@path/to/plant_image.jpg" \
  -F "label=Tomato Plant" \
  -F "additional_info=My plant has been wilting for 3 days"
```

### Using curl for chat:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the signs of overwatering in houseplants?"}'
```

## Development

The project follows a modular structure:
- `services/openai_client.py`: OpenAI integration and model management
- `routes/diagnose/`: Plant diagnosis endpoint
- `routes/chat/`: Chat endpoint
- `main.py`: Flask application setup

## License

This project is for educational and development purposes.
