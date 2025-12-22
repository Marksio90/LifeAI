"""Tests for authentication endpoints."""
import pytest
from fastapi import status


class TestAuthRegistration:
    """Test user registration."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email."""
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "password": "password123",
                "full_name": "Duplicate"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    def test_register_password_too_short(self, client):
        """Test registration with too short password."""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "short",
                "full_name": "User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "full_name": "User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Test user login."""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthProfile:
    """Test profile endpoints."""
    
    def test_get_profile_success(self, client, auth_headers):
        """Test getting user profile."""
        response = client.get("/auth/profile", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without auth."""
        response = client.get("/auth/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_success(self, client, auth_headers):
        """Test updating user profile."""
        response = client.put(
            "/auth/profile",
            headers=auth_headers,
            json={
                "full_name": "Updated Name",
                "preferred_language": "en",
                "preferred_voice": "alloy"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["profile"]["full_name"] == "Updated Name"
        assert data["profile"]["preferred_language"] == "en"
    
    def test_change_password_success(self, client, auth_headers):
        """Test changing password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "password123",
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_change_password_same_as_current(self, client, auth_headers):
        """Test changing password to same password."""
        response = client.post(
            "/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "password123",
                "new_password": "password123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
