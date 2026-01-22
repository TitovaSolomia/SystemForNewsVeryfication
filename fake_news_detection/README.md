# Fake News Detection System

Django-based application designed to analyze news articles and URLs to determine their likely authenticity using a pre-trained machine learning model.

## Features
- URL text extraction via newspaper3k
- Real-time classification using Logistic Regression and TF-IDF
- User authentication and search history tracking
- Modular Javascript frontend with theme support
- Containerized environment using Docker

## Technical Stack
- Framework: Django 5.1
- ML Libraries: Scikit-Learn, Pandas, NumPy
- Database: SQLite 
- Environment: Docker, Docker Compose
- Testing: Pytest

## Setup and Installation

### Docker Installation (Recommended)
1. Ensure Docker Desktop is active.
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
The application will be accessible at http://localhost:8000.

### Manual Installation
1. Initialize virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize database:
   ```bash
   python manage.py migrate
   ```
4. Run server:
   ```bash
   python manage.py runserver
   ```

## Configuration
The application requires an environment file for configuration. Copy `example.env` to `.env` and update the values:
- SECRET_KEY: Django secret key
- DEBUG: Set to True for development
- ALLOWED_HOSTS: List of allowed domains

## Testing
To execute the test suite inside the container:
```bash
docker-compose exec web pytest
```
Testing covers text preprocessing utilities and Django view integration.

## Project Structure
- predictor/: Django application logic and views.
- src/: Core machine learning modules and text cleaning scripts.
- tests/: Integration and unit tests.
- data/: Training datasets and processed CSV files.
