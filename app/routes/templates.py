from flask import Blueprint, request, jsonify
from app.services import template_service
from app.services.email_service import EmailService
from app.exceptions import NotFoundError, ValidationError, EmailTrackerException
from app.services.template_service import TemplateService

template_bp = Blueprint('templates', __name__)

template_service = TemplateService()

@template_bp.route('/', methods=['GET'])
def list_templates():
    return jsonify({'goon'})

@template_bp.route('/', methods=['POST'])
def create_template():
    """
    POST api/emails/templates/

    args:
    template_id, template_name, subject, body

    returns template
    """
    template_id = request.args.get('template_id', type=int)
    template_name = request.args.get('template_id', type=str)
    subject = request.args.get('template_id', type=str)
    body = request.args.get('template_id', type=str)

    return jsonify({'goon'})

@template_bp.route('/<int:template_id>', methods=['GET'])
def get_template():
    
    return jsonify({'goon'})

@template_bp.route('/<int:template_id>', methods=['DELETE'])
def delete_template():
    return jsonify({'goon'})

@template_bp.route('/<int:template_id>', methods=['PUT'])
def update_template():
    return jsonify({'goon'})