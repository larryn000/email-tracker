from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False  # Allow URLs with or without trailing slashes

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import email_bp, campaign_bp, tracking_bp, analytics_bp, template_bp
    app.register_blueprint(email_bp, url_prefix='/api/emails')
    app.register_blueprint(campaign_bp, url_prefix='/api/emails/campaigns')
    app.register_blueprint(tracking_bp, url_prefix='/track')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(template_bp, url_prefix='/api/emails/templates')

    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    # CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database"""
        db.create_all()
        print("Database initialized successfully!")

    @app.cli.command('drop-db')
    def drop_db_command():
        """Drop all database tables"""
        import sys
        if '--force' in sys.argv:
            db.drop_all()
            print("Database dropped successfully!")
        else:
            print("Add --force flag to confirm: flask drop-db --force")

    return app


# Import models to register them with SQLAlchemy
from app import models
