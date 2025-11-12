"""
Tests for the health check endpoint
"""


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test that health check returns 200 with healthy status"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {'status': 'healthy'}
