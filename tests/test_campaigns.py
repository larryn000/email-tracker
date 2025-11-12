"""
Tests for campaign management endpoints
"""


class TestCampaigns:
    """Test campaign endpoints"""

    def test_create_campaign(self, client):
        """Test creating a campaign"""
        response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign',
            'description': 'A test campaign'
        })

        assert response.status_code == 201
        assert 'campaign' in response.json
        assert response.json['campaign']['name'] == 'Test Campaign'

    def test_create_campaign_missing_name(self, client):
        """Test creating a campaign without required name field"""
        response = client.post('/api/emails/campaigns', json={
            'description': 'A test campaign'
        })

        assert response.status_code == 400
        assert 'error' in response.json

    def test_list_campaigns(self, client):
        """Test listing campaigns"""
        # Create a campaign first
        client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })

        response = client.get('/api/emails/campaigns')
        assert response.status_code == 200
        assert 'campaigns' in response.json
        assert len(response.json['campaigns']) == 1

    def test_get_campaign(self, client):
        """Test getting a specific campaign"""
        # Create a campaign first
        create_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign',
            'description': 'Test description'
        })

        campaign_id = create_response.json['campaign']['id']

        response = client.get(f'/api/emails/campaigns/{campaign_id}')
        assert response.status_code == 200
        assert response.json['id'] == campaign_id
        assert response.json['name'] == 'Test Campaign'

    def test_get_campaign_not_found(self, client):
        """Test getting a non-existent campaign"""
        response = client.get('/api/emails/campaigns/99999')
        assert response.status_code == 404

    def test_update_campaign(self, client):
        """Test updating a campaign"""
        # Create a campaign first
        create_response = client.post('/api/emails/campaigns', json={
            'name': 'Original Name',
            'status': 'draft'
        })

        campaign_id = create_response.json['campaign']['id']

        # Update the campaign
        response = client.put(f'/api/emails/campaigns/{campaign_id}', json={
            'name': 'Updated Name',
            'status': 'active'
        })

        assert response.status_code == 200
        assert response.json['campaign']['name'] == 'Updated Name'
        assert response.json['campaign']['status'] == 'active'

    def test_update_campaign_not_found(self, client):
        """Test updating a non-existent campaign"""
        response = client.put('/api/emails/campaigns/99999', json={
            'name': 'Updated Name'
        })
        assert response.status_code == 404

    def test_delete_campaign(self, client):
        """Test deleting a campaign"""
        # Create a campaign first
        create_response = client.post('/api/emails/campaigns', json={
            'name': 'Test Campaign'
        })

        campaign_id = create_response.json['campaign']['id']

        # Delete the campaign
        response = client.delete(f'/api/emails/campaigns/{campaign_id}')
        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f'/api/emails/campaigns/{campaign_id}')
        assert get_response.status_code == 404

    def test_delete_campaign_not_found(self, client):
        """Test deleting a non-existent campaign"""
        response = client.delete('/api/emails/campaigns/99999')
        assert response.status_code == 404
