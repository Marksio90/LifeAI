"""Tests for authentication endpoints."""
import pytest
from fastapi import status


def test_register_success(client, test_user_data):
    """Test successful user registration."""
    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email fails."""
    # First registration
    client.post("/auth/register", json=test_user_data)

    # Second registration with same email
    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user_data):
    """Test successful login."""
    # Register user first
    client.post("/auth/register", json=test_user_data)

    # Login
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password fails."""
    # Register user
    client.post("/auth/register", json=test_user_data)

    # Login with wrong password
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPassword123!"
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user fails."""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(authenticated_client):
    """Test getting current user info."""
    client, _ = authenticated_client

    response = client.get("/auth/me")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "id" in data
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    """Test getting current user without auth fails."""
    response = client.get("/auth/me")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_profile(authenticated_client):
    """Test updating user profile."""
    client, _ = authenticated_client

    response = client.put("/auth/me?full_name=Updated Name&preferred_language=en")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["preferred_language"] == "en"
