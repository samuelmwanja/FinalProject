# YouTube Spam Comment Detector

A machine learning-powered application that analyzes YouTube comments to detect spam. This project uses a trained ML model to classify comments as spam or not spam, helping content creators manage their comments section more effectively.

## Features

- YouTube video URL analysis
- Real-time comment fetching using YouTube API
- ML-based spam detection
- Rule-based fallback classification when ML is unavailable
- User-friendly dashboard for visualizing spam statistics
- Detailed spam comment display with classification confidence

## Tech Stack

### Frontend
- React with TypeScript
- Vite for fast development
- Tailwind CSS for styling

### Backend
- FastAPI (Python) for the API server
- Scikit-learn for machine learning models
- Google YouTube API for fetching comments

## Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- YouTube API key

### Backend Setup

1. Clone this repository
2. Navigate to the project directory
3. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
4. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
5. Run the backend server:
   ```bash
   python -m backend.run_server
   ```
   The server will start on port 7777.

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:5173.

## Usage

1. Navigate to the web application
2. Enter a YouTube video URL in the input field
3. Click "Analyze Comments"
4. View the statistics and detected spam comments

## License

MIT
