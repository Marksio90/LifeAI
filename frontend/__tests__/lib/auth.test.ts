/**
 * Auth Library Tests
 *
 * Tests for authentication utilities.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock implementations for demonstration
// In real implementation, import your actual functions:
// import { setTokens, getAccessToken, clearTokens } from '@/lib/auth';

// Mock functions for this example
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

global.localStorage = mockLocalStorage as any;

const setTokens = (tokens: { access_token: string; refresh_token: string }) => {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
};

const getAccessToken = () => localStorage.getItem('access_token');
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

describe('Auth Library', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('setTokens', () => {
    it('stores access and refresh tokens', () => {
      const tokens = {
        access_token: 'test_access_token',
        refresh_token: 'test_refresh_token'
      };

      setTokens(tokens);

      expect(localStorage.getItem('access_token')).toBe('test_access_token');
      expect(localStorage.getItem('refresh_token')).toBe('test_refresh_token');
    });
  });

  describe('getAccessToken', () => {
    it('retrieves access token from localStorage', () => {
      localStorage.setItem('access_token', 'my_token');

      const token = getAccessToken();

      expect(token).toBe('my_token');
    });

    it('returns null when no token exists', () => {
      const token = getAccessToken();

      expect(token).toBeNull();
    });
  });

  describe('clearTokens', () => {
    it('removes both access and refresh tokens', () => {
      localStorage.setItem('access_token', 'access');
      localStorage.setItem('refresh_token', 'refresh');

      clearTokens();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });
  });
});
