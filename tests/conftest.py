"""
Shared pytest fixtures for all test files

This file is automatically discovered by pytest and makes fixtures
available to all test files in the tests/ directory.
"""

import pytest
from app import create_app, db
from app.models import Email, Campaign, TrackingEvent


@pytest.fixture
def app():
    """
    Create and configure a test Flask app instance

    This fixture:
    - Creates a Flask app with test configuration
    - Uses an in-memory SQLite database (isolated, fast)
    - Creates all database tables before tests
    - Cleans up after each test

    Usage in tests:
        def test_something(app):
            with app.app_context():
                # Do something with app
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Create a Flask test client

    The test client allows you to make HTTP requests to your app
    without running a real server.

    Usage in tests:
        def test_endpoint(client):
            response = client.get('/api/emails')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a Flask CLI test runner

    This allows you to test Flask CLI commands defined with @app.cli.command()

    Usage in tests:
        def test_cli_command(runner):
            result = runner.invoke(args=['init-db'])
            assert result.exit_code == 0
    """
    return app.test_cli_runner()
