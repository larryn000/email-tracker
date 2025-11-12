"""
Tests for email management endpoints
"""


class TestEmails:
    """Test email endpoints"""

    def test_create_email(self, client):
        """Test creating an email"""
        response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'subject': 'Test Email',
            'body': 'Test body'
        })

        assert response.status_code == 201
        assert 'email' in response.json
        assert response.json['email']['recipient_email'] == 'user@example.com'
        assert 'tracking_pixel_url' in response.json
        assert 'tracking_id' in response.json['email']

    def test_create_email_with_campaign(self, client):
        """Test creating an email linked to a campaign"""
        # Create a campaign first
        campaign_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })
        campaign_id = campaign_response.json['campaign']['id']

        # Create email with campaign
        response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'subject': 'Test Email',
            'campaign_id': campaign_id
        })

        assert response.status_code == 201
        assert response.json['email']['campaign_id'] == campaign_id

    def test_create_email_missing_fields(self, client):
        """Test creating an email with missing required fields"""
        response = client.post('/api/emails', json={
            'subject': 'Test Email'
        })

        assert response.status_code == 400
        assert 'error' in response.json
        assert 'missing' in response.json['error'].lower() or 'required' in response.json['error'].lower()

    def test_create_email_invalid_email(self, client):
        """Test creating an email with invalid email format"""
        response = client.post('/api/emails', json={
            'recipient_email': 'invalid-email',
            'sender_email': 'sender@example.com'
        })

        assert response.status_code == 400
        assert 'error' in response.json

    def test_create_email_invalid_campaign(self, client):
        """Test creating an email with non-existent campaign"""
        response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'campaign_id': 99999  # Non-existent campaign
        })

        assert response.status_code == 404
        assert 'error' in response.json

    def test_get_email(self, client):
        """Test getting a specific email"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'subject': 'Test Email'
        })

        email_id = create_response.json['email']['id']

        response = client.get(f'/api/emails/{email_id}')
        assert response.status_code == 200
        assert response.json['id'] == email_id
        assert 'events' in response.json

    def test_get_email_not_found(self, client):
        """Test getting a non-existent email"""
        response = client.get('/api/emails/99999')
        assert response.status_code == 404

    def test_list_emails(self, client):
        """Test listing emails with pagination"""
        # Create multiple emails
        for i in range(3):
            client.post('/api/emails', json={
                'recipient_email': f'user{i}@example.com',
                'sender_email': 'sender@example.com',
                'subject': f'Test Email {i}'
            })

        response = client.get('/api/emails')
        assert response.status_code == 200
        assert 'emails' in response.json
        assert response.json['total'] == 3
        assert len(response.json['emails']) == 3

    def test_list_emails_with_limit(self, client):
        """Test listing emails with limit"""
        # Create multiple emails
        for i in range(5):
            client.post('/api/emails', json={
                'recipient_email': f'user{i}@example.com',
                'sender_email': 'sender@example.com'
            })

        response = client.get('/api/emails?limit=2')
        assert response.status_code == 200
        assert len(response.json['emails']) == 2
        assert response.json['total'] == 5

    def test_list_emails_with_offset(self, client):
        """Test listing emails with offset"""
        # Create multiple emails
        for i in range(5):
            client.post('/api/emails', json={
                'recipient_email': f'user{i}@example.com',
                'sender_email': 'sender@example.com'
            })

        response = client.get('/api/emails?limit=2&offset=2')
        assert response.status_code == 200
        assert len(response.json['emails']) == 2
        assert response.json['offset'] == 2

    def test_list_emails_filter_by_campaign(self, client):
        """Test filtering emails by campaign"""
        # Create campaign
        campaign_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })
        campaign_id = campaign_response.json['campaign']['id']

        # Create emails with and without campaign
        client.post('/api/emails', json={
            'recipient_email': 'user1@example.com',
            'sender_email': 'sender@example.com',
            'campaign_id': campaign_id
        })
        client.post('/api/emails', json={
            'recipient_email': 'user2@example.com',
            'sender_email': 'sender@example.com'
        })

        response = client.get(f'/api/emails?campaign_id={campaign_id}')
        assert response.status_code == 200
        assert response.json['total'] == 1

    def test_list_emails_filter_by_recipient(self, client):
        """Test filtering emails by recipient email"""
        client.post('/api/emails', json={
            'recipient_email': 'user1@example.com',
            'sender_email': 'sender@example.com'
        })
        client.post('/api/emails', json={
            'recipient_email': 'user2@example.com',
            'sender_email': 'sender@example.com'
        })

        response = client.get('/api/emails?recipient_email=user1@example.com')
        assert response.status_code == 200
        assert response.json['total'] == 1
        assert response.json['emails'][0]['recipient_email'] == 'user1@example.com'

    def test_update_email(self, client):
        """Test updating an email"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'subject': 'Original Subject'
        })

        email_id = create_response.json['email']['id']

        # Update the email
        response = client.put(f'/api/emails/{email_id}', json={
            'subject': 'Updated Subject'
        })

        assert response.status_code == 200
        assert response.json['email']['subject'] == 'Updated Subject'

    def test_update_email_not_found(self, client):
        """Test updating a non-existent email"""
        response = client.put('/api/emails/99999', json={
            'subject': 'Updated Subject'
        })
        assert response.status_code == 404

    def test_delete_email(self, client):
        """Test deleting an email"""
        # Create an email first
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        email_id = create_response.json['email']['id']

        # Delete the email
        response = client.delete(f'/api/emails/{email_id}')
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f'/api/emails/{email_id}')
        assert get_response.status_code == 404

    def test_delete_email_cascades_events(self, client):
        """Test that deleting an email also deletes its events"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        email_id = create_response.json['email']['id']
        tracking_id = create_response.json['email']['tracking_id']

        # Create a tracking event
        client.get(f'/track/pixel/{tracking_id}.png')

        # Verify event exists
        events_response = client.get(f'/api/emails/{email_id}/events')
        assert events_response.json['total'] == 1

        # Delete the email
        client.delete(f'/api/emails/{email_id}')

        # Verify email is gone
        get_response = client.get(f'/api/emails/{email_id}')
        assert get_response.status_code == 404

    def test_get_email_events(self, client):
        """Test getting events for a specific email"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        email_id = create_response.json['email']['id']

        response = client.get(f'/api/emails/{email_id}/events')
        assert response.status_code == 200
        assert 'events' in response.json
        assert response.json['email_id'] == email_id

    def test_get_email_events_filter_by_type(self, client):
        """Test filtering email events by type"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        email_id = create_response.json['email']['id']
        tracking_id = create_response.json['email']['tracking_id']

        # Create different event types
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/click/{tracking_id}?url=https://example.com')

        # Filter by event type
        response = client.get(f'/api/emails/{email_id}/events?event_type=open')
        assert response.status_code == 200
        assert response.json['total'] == 1
        assert response.json['events'][0]['event_type'] == 'open'
