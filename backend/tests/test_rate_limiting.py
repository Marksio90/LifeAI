"""Tests for rate limiting."""
import pytest
from fastapi import status
from unittest.mock import Mock, patch


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @patch('app.middleware.rate_limit.redis_client')
    def test_login_rate_limit(self, mock_redis, client, test_user):
        """Test that login endpoint is rate limited."""
        # Mock Redis to simulate hitting rate limit
        mock_redis.get.return_value = "5"  # Already at limit
        mock_redis.ttl.return_value = 60  # 60 seconds until reset
        
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        # Should return 429 when rate limit hit
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in response.headers
    
    @patch('app.middleware.rate_limit.redis_client')
    def test_rate_limit_allows_under_limit(self, mock_redis, client, test_user):
        """Test that requests under limit are allowed."""
        # Mock Redis to show we're under the limit
        mock_redis.get.return_value = "3"  # Under limit of 5
        mock_redis.incr.return_value = 4
        
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        # Should succeed when under rate limit
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
        # (401 is also valid if password is wrong, point is it's not 429)
    
    @patch('app.middleware.rate_limit.redis_client')
    def test_rate_limit_first_request(self, mock_redis, client, test_user):
        """Test that first request sets up rate limit counter."""
        # Mock Redis to show no previous requests
        mock_redis.get.return_value = None
        
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        # Should succeed and set counter
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
        mock_redis.setex.assert_called_once()
