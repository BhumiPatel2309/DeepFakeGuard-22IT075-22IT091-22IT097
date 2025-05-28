# DeepFakeGuard - DeepFake Detection System

A comprehensive deepfake detection system that uses advanced machine learning techniques to identify and protect against deepfake content.

## Features

- Real-time deepfake detection for images and videos
- Google Single Sign-On (SSO) authentication
- User-friendly Streamlit web interface
- Support for multiple image and video formats
- Database integration for user management and detection history

## Prerequisites

- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- Google Cloud Account (for SSO setup)

## Installation

### Using Docker (Recommended)

1. Build the Docker image:
```bash
docker build -t deepfakeguard .
```

2. Run the container:
```bash
docker-compose up
```

### Local Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file with the following variables:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
DATABASE_URL=sqlite:///deepfake.db
```

2. Set up Google SSO:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google+ API
   - Create OAuth 2.0 Client ID
   - Set authorized redirect URI to: http://localhost:8501

## Running the Application

### Using Docker
```bash
docker-compose up
```

### Local Development
```bash
streamlit run app.py
```

The application will be available at: http://localhost:8501

## Project Structure

```
DeepFakeGuard/
├── .streamlit/          # Streamlit configuration
├── api.py              # API endpoints
├── app.py              # Main application file
├── architectures/      # Model architectures
├── blazeface/          # Face detection module
├── config.py           # Configuration settings
├── database/           # Database models and migrations
├── image.py            # Image processing utilities
├── isplutils/          # Image processing utilities
├── src/                # Source code
├── tests/              # Test files
└── uploads/            # User uploaded files
```

## Testing

To run the test suite:
```bash
pytest tests/
```

## Security

- All user sessions are protected with CSRF tokens
- Google SSO implementation includes state verification
- User data is stored securely in the database
- Environment variables are used for sensitive configuration

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

