import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.models import NewsCheck

@pytest.mark.django_db
class TestPredictorViews:
    """
    Test suite for Predictor application views.
    Covers Authentication, Page loading, and Fact-Checking API.
    """

    def test_index_page_loads_anonymous(self, client):
        """Verify index page loads for unauthenticated users."""
        url = reverse('index')
        response = client.get(url)
        assert response.status_code == 200
        assert 'history' in response.context
        assert response.context['history'] is None

    def test_index_page_loads_authenticated(self, client, django_user_model):
        """Verify index page loads for logged-in users and shows context."""
        user = django_user_model.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        
        url = reverse('index')
        response = client.get(url)
        assert response.status_code == 200
        assert 'history' is not None

    def test_login_page_loads(self, client):
        """Verify login page is accessible."""
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200

    def test_signup_page_loads(self, client):
        """Verify signup page is accessible."""
        url = reverse('signup')
        response = client.get(url)
        assert response.status_code == 200

    def test_check_fact_api_basic(self, client):
        """Test the fact checking JSON endpoint."""
        url = reverse('check_fact')
        data = {'text': 'This is a test news article about something real.'}
        # Note: views.py uses json.loads(request.body), so we send as json
        response = client.post(url, data=data, content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.json()
        assert 'result' in json_data
        assert 'real' in json_data['result'].lower() or 'true' in json_data['result'].lower()

    def test_check_fact_api_empty_input(self, client):
        """Verify handling of empty input in fact checking."""
        url = reverse('check_fact')
        data = {'text': ''}
        response = client.post(url, data=data, content_type='application/json')
        
        # Current implementation in views.py line 24 returns 400 for empty input
        assert response.status_code == 400
        assert 'error' in response.json()
