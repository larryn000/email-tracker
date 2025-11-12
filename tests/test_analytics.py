"""
Tests for analytics endpoints
"""


class TestAnalytics:
    """Test analytics endpoints"""

    def test_analytics_overview_empty(self, client):
        """Test analytics overview with no data"""
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        assert response.json['total_emails'] == 0
        assert response.json['total_opens'] == 0
        assert response.json['open_rate'] == 0

    def test_analytics_overview_with_data(self, client):
        """Test analytics overview with email data"""
        # Create emails
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track an open
        client.get(f'/track/pixel/{tracking_id}.png')

        # Get analytics
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        assert response.json['total_emails'] == 1
        assert response.json['total_opens'] == 1
        assert response.json['unique_opens'] == 1

    def test_analytics_overview_multiple_opens_same_email(self, client):
        """Test analytics differentiates between total and unique opens"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track multiple opens of same email
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/pixel/{tracking_id}.png')

        # Get analytics
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        assert response.json['total_opens'] == 3
        assert response.json['unique_opens'] == 1  # Only 1 unique email opened

    def test_analytics_overview_with_clicks(self, client):
        """Test analytics includes click tracking"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        tracking_id = create_response.json['email']['tracking_id']

        # Track opens and clicks
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/click/{tracking_id}?url=https://example.com')

        # Get analytics
        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        assert response.json['total_opens'] == 1
        assert response.json['total_clicks'] == 1
        assert response.json['click_rate'] == 100.0  # 1 click / 1 email

    def test_analytics_overview_filter_by_campaign(self, client):
        """Test analytics filtered by campaign"""
        # Create campaign
        campaign_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })
        campaign_id = campaign_response.json['campaign']['id']

        # Create emails in and out of campaign
        in_campaign = client.post('/api/emails', json={
            'recipient_email': 'user1@example.com',
            'sender_email': 'sender@example.com',
            'campaign_id': campaign_id
        })
        out_campaign = client.post('/api/emails', json={
            'recipient_email': 'user2@example.com',
            'sender_email': 'sender@example.com'
        })

        # Track opens
        client.get(f'/track/pixel/{in_campaign.json["email"]["tracking_id"]}.png')
        client.get(f'/track/pixel/{out_campaign.json["email"]["tracking_id"]}.png')

        # Get campaign-filtered analytics
        response = client.get(f'/api/analytics/overview?campaign_id={campaign_id}')
        assert response.status_code == 200
        assert response.json['total_emails'] == 1
        assert response.json['total_opens'] == 1

    def test_email_analytics(self, client):
        """Test email analytics endpoint"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'subject': 'Test Email'
        })

        email_id = create_response.json['email']['id']

        response = client.get(f'/api/analytics/email/{email_id}')
        assert response.status_code == 200
        assert response.json['email_id'] == email_id
        assert 'total_opens' in response.json
        assert 'total_clicks' in response.json
        assert 'device_breakdown' in response.json

    def test_email_analytics_with_events(self, client):
        """Test email analytics with tracking events"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'subject': 'Test Email'
        })

        email_id = create_response.json['email']['id']
        tracking_id = create_response.json['email']['tracking_id']

        # Track events
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/pixel/{tracking_id}.png')
        client.get(f'/track/click/{tracking_id}?url=https://example.com')

        response = client.get(f'/api/analytics/email/{email_id}')
        assert response.status_code == 200
        assert response.json['total_opens'] == 2
        assert response.json['total_clicks'] == 1
        assert response.json['first_opened_at'] is not None
        assert response.json['last_opened_at'] is not None

    def test_email_analytics_not_found(self, client):
        """Test email analytics with non-existent email"""
        response = client.get('/api/analytics/email/99999')
        assert response.status_code == 404

    def test_email_analytics_device_breakdown(self, client):
        """Test device breakdown in email analytics"""
        # Create an email
        create_response = client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com'
        })

        email_id = create_response.json['email']['id']
        tracking_id = create_response.json['email']['tracking_id']

        # Track events (user-agent header would determine device type in real scenario)
        client.get(f'/track/pixel/{tracking_id}.png')

        response = client.get(f'/api/analytics/email/{email_id}')
        assert response.status_code == 200
        assert 'device_breakdown' in response.json
        assert isinstance(response.json['device_breakdown'], dict)

    def test_campaign_analytics(self, client):
        """Test campaign analytics endpoint"""
        # Create campaign
        campaign_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })
        campaign_id = campaign_response.json['campaign']['id']

        # Create email in campaign
        client.post('/api/emails', json={
            'recipient_email': 'user@example.com',
            'sender_email': 'sender@example.com',
            'campaign_id': campaign_id
        })

        response = client.get(f'/api/analytics/campaign/{campaign_id}')
        assert response.status_code == 200
        assert response.json['campaign_id'] == campaign_id
        assert response.json['total_emails'] == 1

    def test_campaign_analytics_with_events(self, client):
        """Test campaign analytics with tracking data"""
        # Create campaign
        campaign_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })
        campaign_id = campaign_response.json['campaign']['id']

        # Create multiple emails in campaign
        for i in range(3):
            email_response = client.post('/api/emails', json={
                'recipient_email': f'user{i}@example.com',
                'sender_email': 'sender@example.com',
                'campaign_id': campaign_id
            })

            tracking_id = email_response.json['email']['tracking_id']

            # Track some events
            if i < 2:  # Only 2 out of 3 emails opened
                client.get(f'/track/pixel/{tracking_id}.png')
            if i < 1:  # Only 1 out of 3 emails clicked
                client.get(f'/track/click/{tracking_id}?url=https://example.com')

        response = client.get(f'/api/analytics/campaign/{campaign_id}')
        assert response.status_code == 200
        assert response.json['total_emails'] == 3
        assert response.json['unique_opens'] == 2
        assert response.json['total_clicks'] == 1
        assert response.json['open_rate'] == round(2/3 * 100, 2)  # 66.67%

    def test_campaign_analytics_not_found(self, client):
        """Test campaign analytics with non-existent campaign"""
        response = client.get('/api/analytics/campaign/99999')
        assert response.status_code == 404

    def test_campaign_analytics_empty_campaign(self, client):
        """Test campaign analytics for campaign with no emails"""
        # Create empty campaign
        campaign_response = client.post('/api/emails/campaigns', json={
            'name': 'Empty Campaign'
        })
        campaign_id = campaign_response.json['campaign']['id']

        response = client.get(f'/api/analytics/campaign/{campaign_id}')
        assert response.status_code == 200
        assert response.json['total_emails'] == 0
        assert response.json['total_opens'] == 0
        assert response.json['open_rate'] == 0

    def test_analytics_open_rate_calculation(self, client):
        """Test open rate is calculated correctly"""
        # Create 10 emails
        for i in range(10):
            email_response = client.post('/api/emails', json={
                'recipient_email': f'user{i}@example.com',
                'sender_email': 'sender@example.com'
            })

            # Only open 5 of them
            if i < 5:
                tracking_id = email_response.json['email']['tracking_id']
                client.get(f'/track/pixel/{tracking_id}.png')

        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        assert response.json['total_emails'] == 10
        assert response.json['unique_opens'] == 5
        assert response.json['open_rate'] == 50.0  # 5/10 = 50%

    def test_analytics_click_rate_calculation(self, client):
        """Test click rate is calculated correctly"""
        # Create 10 emails
        for i in range(10):
            email_response = client.post('/api/emails', json={
                'recipient_email': f'user{i}@example.com',
                'sender_email': 'sender@example.com'
            })

            tracking_id = email_response.json['email']['tracking_id']

            # Click on 3 of them
            if i < 3:
                client.get(f'/track/click/{tracking_id}?url=https://example.com')

        response = client.get('/api/analytics/overview')
        assert response.status_code == 200
        assert response.json['total_emails'] == 10
        assert response.json['total_clicks'] == 3
        assert response.json['click_rate'] == 30.0  # 3/10 = 30%
