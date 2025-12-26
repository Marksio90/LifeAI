"""Tests for Sentry monitoring integration."""
import pytest
from unittest.mock import patch, Mock, MagicMock
from app.monitoring.sentry import (
    init_sentry,
    capture_exception,
    capture_message,
    set_user_context,
    clear_user_context,
    add_breadcrumb,
    before_send_filter
)
from app.core.config import Settings


class TestSentryInitialization:
    """Test suite for Sentry initialization."""

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_init_sentry_with_dsn(self, mock_sdk):
        """Test Sentry initialization with valid DSN."""
        settings = Settings()
        settings.sentry_dsn = "https://test@sentry.io/123"
        settings.sentry_environment = "test"
        settings.sentry_traces_sample_rate = 1.0
        settings.sentry_profiles_sample_rate = 1.0
        settings.app_version = "2.1.0"

        init_sentry(settings)

        # Verify init was called
        mock_sdk.init.assert_called_once()

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_init_sentry_without_dsn(self, mock_sdk):
        """Test Sentry skips initialization without DSN."""
        settings = Settings()
        settings.sentry_dsn = ""

        init_sentry(settings)

        # Init should not be called
        mock_sdk.init.assert_not_called()

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_init_sentry_production_sample_rates(self, mock_sdk):
        """Test that production has reduced sample rates."""
        settings = Settings()
        settings.sentry_dsn = "https://test@sentry.io/123"
        settings.environment = "production"
        settings.sentry_traces_sample_rate = 1.0  # Will be adjusted

        # Load should adjust rates for production
        settings = Settings.load() if hasattr(Settings, 'load') else settings

        # In production, rates should be lower
        if settings.environment == "production":
            assert settings.sentry_traces_sample_rate <= 0.1


class TestSentryExceptionCapture:
    """Test suite for exception capture."""

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_capture_exception_basic(self, mock_sdk):
        """Test capturing a basic exception."""
        mock_sdk.capture_exception.return_value = "test-event-id"

        try:
            raise ValueError("Test error")
        except ValueError as e:
            event_id = capture_exception(e)

        assert event_id == "test-event-id"
        mock_sdk.capture_exception.assert_called_once()

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_capture_exception_with_context(self, mock_sdk):
        """Test capturing exception with additional context."""
        mock_sdk.capture_exception.return_value = "test-event-id"
        mock_sdk.push_scope.return_value.__enter__ = Mock()
        mock_sdk.push_scope.return_value.__exit__ = Mock()

        context = {
            "user_id": "test-user",
            "operation": "test_operation"
        }

        try:
            raise RuntimeError("Test error")
        except RuntimeError as e:
            event_id = capture_exception(e, context=context)

        assert event_id is not None


class TestSentryMessageCapture:
    """Test suite for message capture."""

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_capture_message_info(self, mock_sdk):
        """Test capturing info message."""
        mock_sdk.capture_message.return_value = "test-message-id"

        event_id = capture_message("Test message", level="info")

        assert event_id == "test-message-id"
        mock_sdk.capture_message.assert_called_once()

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_capture_message_warning(self, mock_sdk):
        """Test capturing warning message."""
        mock_sdk.capture_message.return_value = "test-warning-id"

        event_id = capture_message("Warning message", level="warning")

        assert event_id is not None
        # Verify level was passed
        call_args = mock_sdk.capture_message.call_args
        assert call_args[1]["level"] == "warning"

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_capture_message_with_context(self, mock_sdk):
        """Test capturing message with context."""
        mock_sdk.capture_message.return_value = "test-id"
        mock_sdk.push_scope.return_value.__enter__ = Mock()
        mock_sdk.push_scope.return_value.__exit__ = Mock()

        context = {"test_key": "test_value"}
        event_id = capture_message("Test", level="info", context=context)

        assert event_id is not None


class TestSentryUserContext:
    """Test suite for user context tracking."""

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_set_user_context(self, mock_sdk):
        """Test setting user context."""
        set_user_context(
            user_id="user-123",
            email="test@example.com",
            username="testuser"
        )

        mock_sdk.set_user.assert_called_once_with({
            "id": "user-123",
            "email": "test@example.com",
            "username": "testuser"
        })

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_set_user_context_partial(self, mock_sdk):
        """Test setting user context with partial data."""
        set_user_context(user_id="user-123")

        mock_sdk.set_user.assert_called_once()
        call_args = mock_sdk.set_user.call_args[0][0]
        assert call_args["id"] == "user-123"
        assert call_args["email"] is None

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_clear_user_context(self, mock_sdk):
        """Test clearing user context."""
        clear_user_context()

        mock_sdk.set_user.assert_called_once_with(None)


class TestSentryBreadcrumbs:
    """Test suite for breadcrumb tracking."""

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_add_breadcrumb_basic(self, mock_sdk):
        """Test adding a basic breadcrumb."""
        add_breadcrumb("Test event", category="test")

        mock_sdk.add_breadcrumb.assert_called_once()

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_add_breadcrumb_with_data(self, mock_sdk):
        """Test adding breadcrumb with data."""
        add_breadcrumb(
            "Database query",
            category="db",
            level="info",
            data={"query": "SELECT * FROM users", "duration": 150}
        )

        mock_sdk.add_breadcrumb.assert_called_once()
        call_args = mock_sdk.add_breadcrumb.call_args
        assert call_args[1]["category"] == "db"
        assert "query" in call_args[1]["data"]


class TestBeforeSendFilter:
    """Test suite for before_send filter."""

    def test_filter_http_404(self):
        """Test that HTTP 404 errors are filtered."""
        event = {}
        hint = {
            'exc_info': (
                type(None),
                Mock(status_code=404),
                None
            )
        }

        result = before_send_filter(event, hint)

        # 404 should be filtered (return None)
        assert result is None

    def test_filter_password_field(self):
        """Test that password fields are filtered."""
        event = {
            'request': {
                'data': {
                    'username': 'test',
                    'password': 'secret123',
                    'email': 'test@example.com'
                }
            }
        }
        hint = {}

        result = before_send_filter(event, hint)

        # Password should be filtered
        assert result['request']['data']['password'] == '[FILTERED]'
        assert result['request']['data']['username'] == 'test'

    def test_filter_token_field(self):
        """Test that token fields are filtered."""
        event = {
            'request': {
                'data': {
                    'token': 'secret-token-123'
                }
            }
        }
        hint = {}

        result = before_send_filter(event, hint)

        assert result['request']['data']['token'] == '[FILTERED]'

    def test_filter_api_key_field(self):
        """Test that API key fields are filtered."""
        event = {
            'request': {
                'data': {
                    'api_key': 'sk-123456789'
                }
            }
        }
        hint = {}

        result = before_send_filter(event, hint)

        assert result['request']['data']['api_key'] == '[FILTERED]'

    def test_filter_keyboard_interrupt(self):
        """Test that KeyboardInterrupt is filtered."""
        event = {}
        hint = {
            'exc_info': (
                KeyboardInterrupt,
                KeyboardInterrupt(),
                None
            )
        }

        result = before_send_filter(event, hint)

        # Should be filtered
        assert result is None

    def test_add_custom_tags(self):
        """Test that custom tags are added."""
        event = {
            'user': {
                'id': 'user-123'
            }
        }
        hint = {}

        result = before_send_filter(event, hint)

        # Custom tag should be added
        assert 'tags' in result
        assert 'user_authenticated' in result['tags']
        assert result['tags']['user_authenticated'] is True


class TestSentryIntegration:
    """Integration tests for Sentry."""

    @patch('app.monitoring.sentry.sentry_sdk')
    def test_full_error_tracking_flow(self, mock_sdk):
        """Test complete error tracking flow."""
        mock_sdk.capture_exception.return_value = "event-123"
        mock_sdk.push_scope.return_value.__enter__ = Mock()
        mock_sdk.push_scope.return_value.__exit__ = Mock()

        # Set user context
        set_user_context(user_id="user-456", email="user@test.com")

        # Add breadcrumb
        add_breadcrumb("User action", category="action")

        # Capture exception
        try:
            raise ValueError("Test error")
        except ValueError as e:
            event_id = capture_exception(e, context={"page": "test_page"})

        # Verify all calls were made
        assert mock_sdk.set_user.called
        assert mock_sdk.add_breadcrumb.called
        assert mock_sdk.capture_exception.called
        assert event_id is not None
