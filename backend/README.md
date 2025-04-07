# YouTube Spam Detection Backend

This is the backend service for the YouTube Spam Detection application, built with FastAPI and ML-powered spam classification.

## Setup

1. Make sure you have Python 3.8+ installed
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## Running the Application

### Test the Spam Classifier

To test the spam classifier with sample comments:
```
python test_classifier.py
```

### Run the API Server

To start the API server:
```
python run.py
```

The API will be available at http://localhost:8000

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Spam Detection

- `POST /api/v1/spam-detection/classify`: Classify a single comment for spam
- `POST /api/v1/spam-detection/classify_batch`: Classify multiple comments
- `POST /api/v1/spam-detection/classify_youtube_comments`: Classify YouTube comments

## Development

To run in development mode with auto-reload:
```
uvicorn backend.app.main:app --reload
```

## YouTube Spam Comment Detection

This API provides tools to analyze and classify YouTube comments for spam detection.

### Features

- ML-based spam detection with pre-trained models
- Rule-based fallback classification when ML model is unavailable
- YouTube comments fetching and analysis
- Dashboard metrics for spam monitoring

> **Note**: The system now uses pre-trained ML models as the primary method for classifying spam and non-spam comments. The rule-based detection is only used as a fallback when the ML model is unavailable. 