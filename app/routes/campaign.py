from flask import Blueprint, request, jsonify
from app.services.campaign_service import CampaignService
from app.exceptions import NotFoundError, ValidationError, EmailTrackerException

# Blueprint for campaign management
campaign_bp = Blueprint('campaigns', __name__)

# Initialize service
campaign_service = CampaignService()


@campaign_bp.route('/', methods=['GET'])
def list_campaigns():
    """
    GET /api/emails/campaigns
    List all campaigns
    Query params: status, created_by, limit, offset
    """
    try:
        status = request.args.get('status')
        created_by = request.args.get('created_by')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Validate limit and offset
        if limit < 1 or limit > 100:
            return jsonify({'error': 'limit must be between 1 and 100'}), 400

        if offset < 0:
            return jsonify({'error': 'offset must be non-negative'}), 400

        # Use service to list campaigns
        campaigns = campaign_service.list_campaigns(
            status=status,
            created_by=created_by,
            limit=limit,
            offset=offset
        )

        return jsonify({
            'campaigns': [campaign.to_dict() for campaign in campaigns],
            'total': len(campaigns)
        }), 200

    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@campaign_bp.route('/', methods=['POST'])
def create_campaign():
    """
    POST /api/emails/campaigns
    Create a new campaign
    Body: {
        "name": "Campaign name",
        "description": "Campaign description",
        "created_by": "user@example.com",
        "status": "draft"
    }
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'name is required'}), 400

        # Use service to create campaign
        campaign = campaign_service.create_campaign(
            name=data['name'],
            description=data.get('description'),
            created_by=data.get('created_by'),
            status=data.get('status', 'draft')
        )

        return jsonify({
            'message': 'Campaign created successfully',
            'campaign': campaign.to_dict()
        }), 201

    except ValidationError as e:
        return jsonify({'error': str(e), 'field': e.field}), 400
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """
    GET /api/emails/campaigns/<id>
    Get a specific campaign with all emails
    """
    try:
        campaign = campaign_service.get_campaign(campaign_id)

        campaign_data = campaign.to_dict()
        campaign_data['emails'] = [email.to_dict() for email in campaign.emails.all()]

        return jsonify(campaign_data), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """
    PUT /api/emails/campaigns/<id>
    Update a campaign
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Use service to update campaign
        campaign = campaign_service.update_campaign(
            campaign_id=campaign_id,
            name=data.get('name'),
            description=data.get('description'),
            status=data.get('status'),
            created_by=data.get('created_by')
        )

        return jsonify({
            'message': 'Campaign updated successfully',
            'campaign': campaign.to_dict()
        }), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        return jsonify({'error': str(e), 'field': e.field}), 400
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """
    DELETE /api/emails/campaigns/<id>
    Delete a campaign (emails will have campaign_id set to null)
    """
    try:
        campaign_service.delete_campaign(campaign_id)

        return jsonify({'message': 'Campaign deleted successfully'}), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
