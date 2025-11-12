"""
Tests for Flask CLI commands
"""

from app import db
from app.models import Email, Campaign, TrackingEvent


class TestCLI:
    """Test CLI commands"""

    def test_init_db_command(self, runner, app):
        """Test the init-db CLI command"""
        with app.app_context():
            # Drop tables first to ensure clean state
            db.drop_all()

        result = runner.invoke(args=['init-db'])

        # Print debug info if test fails
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            if result.exception:
                print(f"Exception: {result.exception}")

        assert result.exit_code == 0
        assert 'Database initialized successfully!' in result.output

        # Verify tables were created
        with app.app_context():
            # Check if tables exist by trying to query them
            assert Email.query.count() == 0  # Should work if table exists
            assert Campaign.query.count() == 0
            assert TrackingEvent.query.count() == 0
