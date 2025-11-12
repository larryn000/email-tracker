#!/usr/bin/env python3
"""
Email Tracker Application Entry Point

This script runs the Flask development server.
For production, use a WSGI server like gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
"""

from app import create_app, db
from app.models import Email, TrackingEvent, Campaign

# Create Flask application instance
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Make database and models available in Flask shell
    Usage: flask shell
    """
    return {
        'db': db,
        'Email': Email,
        'TrackingEvent': TrackingEvent,
        'Campaign': Campaign
    }


@app.cli.command()
def init_db():
    """
    Initialize the database
    Usage: flask init-db
    """
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def drop_db():
    """
    Drop all database tables
    Usage: flask drop-db
    WARNING: This will delete all data!
    """
    confirm = input("Are you sure you want to drop all tables? (yes/no): ")
    if confirm.lower() == 'yes':
        db.drop_all()
        print("Database dropped successfully!")
    else:
        print("Operation cancelled.")


if __name__ == '__main__':
    # Run development server
    # Debug mode is enabled - DO NOT use in production!
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,        # Port number
        debug=True        # Enable debug mode (auto-reload, detailed errors)
    )
