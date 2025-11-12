from flask import Blueprint, request, jsonify
from app.services.analytics_service import AnalyticsService
from app.exceptions import NotFoundError, ValidationError, EmailTrackerException

# Blueprint for analytics
analytics_bp = Blueprint('analytics', __name__)

# Initialize service
analytics_service = AnalyticsService()


@analytics_bp.route('/overview', methods=['GET'])
def analytics_overview():
    """
    GET /api/analytics/overview
    Get overall analytics summary (global stats)
    Query params: campaign_id (optional, filter by campaign)
    """
    try:
        campaign_id = request.args.get('campaign_id', type=int)

        if campaign_id:
            # Get campaign-specific stats
            stats = analytics_service.get_campaign_stats(campaign_id)
        else:
            # Get global stats
            stats = analytics_service.get_global_stats()

        return jsonify(stats), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@analytics_bp.route('/email/<int:email_id>', methods=['GET'])
def email_analytics(email_id):
    """
    GET /api/analytics/email/<id>
    Get detailed analytics for a specific email
    """
    try:
        stats = analytics_service.get_email_stats(email_id)

        return jsonify(stats), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@analytics_bp.route('/campaign/<int:campaign_id>', methods=['GET'])
def campaign_analytics(campaign_id):
    """
    GET /api/analytics/campaign/<id>
    Get analytics for all emails in a campaign
    """
    try:
        stats = analytics_service.get_campaign_stats(campaign_id)

        return jsonify(stats), 200

    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@analytics_bp.route('/top-campaigns', methods=['GET'])
def top_performing_campaigns():
    """
    GET /api/analytics/top-campaigns
    Get top performing campaigns
    Query params: limit (default 10), metric (open_rate|click_rate|total_opens|total_clicks)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        metric = request.args.get('metric', 'open_rate')

        # Validate limit
        if limit < 1 or limit > 100:
            return jsonify({'error': 'limit must be between 1 and 100'}), 400

        top_campaigns = analytics_service.get_top_performing_campaigns(limit=limit, metric=metric)

        return jsonify({
            'campaigns': top_campaigns,
            'metric': metric,
            'limit': limit
        }), 200

    except EmailTrackerException as e:
        return jsonify({'error': str(e), 'field': e.field}), e.status_code
    except ValueError as e:
        return jsonify({'error': 'Invalid parameter type', 'details': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
