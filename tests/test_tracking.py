"""
Tests for tracking endpoints (pixel and link tracking)
"""


class TestTracking:
    """Test tracking endpoints"""

    def test_track_pixel(self, client):
        """Test tracking pixel endpoint"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Request the tracking pixel
        response = client.get(f'/track/pixel/{tracking_id}.png')
        assert response.status_code == 200
        assert response.content_type == 'image/png'

        # Verify event was created
        email_id = create_response.json['email']['id']
        events_response = client.get(f'/api/emails/{email_id}/events')
        assert events_response.json['total'] == 1
        assert events_response.json['events'][0]['event_type'] == 'open'

    def test_track_pixel_multiple_opens(self, client):
        """Test tracking multiple opens of the same email"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']
        email_id = create_response.json['email']['id']

        # Track multiple opens
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/pixel/{tracking_id}.png')

        # Verify all events were recorded
        events_response = client.get(f'/api/emails/{email_id}/events')
        assert events_response.json['total'] == 3

    def test_track_pixel_invalid_tracking_id(self, client):
        """Test tracking pixel with invalid tracking ID"""
        # Should still return a pixel (don't reveal which IDs are valid)
        response = client.get('/track/pixel/invalid123.png')
        assert response.status_code == 200
        assert response.content_type == 'image/png'

    def test_track_click(self, client):
        """Test link click tracking"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track a click
        response = client.get(
            f'/track/click/{tracking_id}',
            query_string={'url': 'https://example.com'},
            follow_redirects=False
        )

        assert response.status_code == 302
        assert response.location == 'https://example.com'

        # Verify event was created
        email_id = create_response.json['email']['id']
        events_response = client.get(f'/api/emails/{email_id}/events?event_type=click')
        assert events_response.json['total'] == 1
        assert events_response.json['events'][0]['clicked_url'] == 'https://example.com'

    def test_track_click_multiple_urls(self, client):
        """Test tracking clicks on different URLs"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']
        email_id = create_response.json['email']['id']

        # Track clicks on different URLs
        client.get(
            f'/track/click/{tracking_id}',
            query_string={'url': 'https://example.com'},
            follow_redirects=False
        )
        client.get(
            f'/track/click/{tracking_id}',
            query_string={'url': 'https://another-site.com'},
            follow_redirects=False
        )

        # Verify both clicks were recorded
        events_response = client.get(f'/api/emails/{email_id}/events?event_type=click')
        assert events_response.json['total'] == 2

    def test_track_click_invalid_url(self, client):
        """Test click tracking with invalid URL"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track a click with invalid URL
        response = client.get(
            f'/track/click/{tracking_id}',
            query_string={'url': 'not-a-valid-url'},
            follow_redirects=False
        )

        assert response.status_code == 400

    def test_track_click_default_url(self, client):
        """Test click tracking without URL parameter (should redirect to /)"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track a click without URL
        response = client.get(
            f'/track/click/{tracking_id}',
            follow_redirects=False
        )

        assert response.status_code == 302
        assert response.location == '/'

    def test_track_click_invalid_tracking_id(self, client):
        """Test click tracking with invalid tracking ID"""
        # Should still redirect (don't reveal which IDs are valid)
        response = client.get(
            '/track/click/invalid123',
            query_string={'url': 'https://example.com'},
            follow_redirects=False
        )

        assert response.status_code == 302
        assert response.location == 'https://example.com'

    def test_track_custom_event(self, client):
        """Test custom event tracking"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track custom event
        response = client.post('/track/event', json={
            'tracking_id': tracking_id,
            'event_type': 'bounce'
        })

        assert response.status_code == 201
        assert response.json['event']['event_type'] == 'bounce'

    def test_track_custom_event_missing_fields(self, client):
        """Test custom event tracking with missing fields"""
        response = client.post('/track/event', json={
            'tracking_id': 'abc123'
        })

        assert response.status_code == 400
        assert 'error' in response.json

    def test_track_custom_event_missing_tracking_id(self, client):
        """Test custom event tracking without tracking ID"""
        response = client.post('/track/event', json={
            'event_type': 'bounce'
        })

        assert response.status_code == 400
        assert 'error' in response.json

    def test_track_custom_event_invalid_tracking_id(self, client):
        """Test custom event tracking with non-existent tracking ID"""
        response = client.post('/track/event', json={
            'tracking_id': 'invalid123',
            'event_type': 'bounce'
        })

        assert response.status_code == 404

    def test_track_custom_event_types(self, client):
        """Test tracking various custom event types"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']
        email_id = create_response.json['email']['id']

        # Track different event types
        event_types = ['bounce', 'unsubscribe', 'spam_report', 'delivered']

        for event_type in event_types:
            response = client.post('/track/event', json={
                'tracking_id': tracking_id,
                'event_type': event_type
            })
            assert response.status_code == 201

        # Verify all events were recorded
        events_response = client.get(f'/api/emails/{email_id}/events')
        assert events_response.json['total'] == 4
