"use client";

import { useEffect, useState } from "react";
import { getAccessToken, getRefreshToken } from "@/lib/auth";

export default function DebugPage() {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [tokenPayload, setTokenPayload] = useState<any>(null);

  useEffect(() => {
    // Get tokens from localStorage
    const access = getAccessToken();
    const refresh = getRefreshToken();

    setAccessToken(access);
    setRefreshToken(refresh);

    // Try to decode the access token (JWT)
    if (access) {
      try {
        const parts = access.split('.');
        if (parts.length === 3) {
          const payload = JSON.parse(atob(parts[1]));
          setTokenPayload(payload);
        }
      } catch (e) {
        console.error('Error decoding token:', e);
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Authentication Debug
        </h1>

        <div className="space-y-6">
          {/* Access Token */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Access Token
            </h2>
            {accessToken ? (
              <>
                <p className="text-sm text-green-600 dark:text-green-400 mb-2">
                  ✓ Token found in localStorage
                </p>
                <textarea
                  className="w-full p-3 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-xs rounded"
                  rows={4}
                  value={accessToken}
                  readOnly
                />
              </>
            ) : (
              <p className="text-sm text-red-600 dark:text-red-400">
                ✗ No access token found in localStorage
              </p>
            )}
          </div>

          {/* Token Payload */}
          {tokenPayload && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Token Payload
              </h2>
              <pre className="w-full p-3 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-xs rounded overflow-x-auto">
                {JSON.stringify(tokenPayload, null, 2)}
              </pre>

              {/* Check expiration */}
              {tokenPayload.exp && (
                <div className="mt-4">
                  <p className="text-sm">
                    <span className="font-semibold">Expires:</span>{" "}
                    {new Date(tokenPayload.exp * 1000).toLocaleString()}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">Is Expired:</span>{" "}
                    {Date.now() > tokenPayload.exp * 1000 ? (
                      <span className="text-red-600 dark:text-red-400">Yes ✗</span>
                    ) : (
                      <span className="text-green-600 dark:text-green-400">No ✓</span>
                    )}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Refresh Token */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Refresh Token
            </h2>
            {refreshToken ? (
              <>
                <p className="text-sm text-green-600 dark:text-green-400 mb-2">
                  ✓ Token found in localStorage
                </p>
                <textarea
                  className="w-full p-3 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-xs rounded"
                  rows={4}
                  value={refreshToken}
                  readOnly
                />
              </>
            ) : (
              <p className="text-sm text-red-600 dark:text-red-400">
                ✗ No refresh token found in localStorage
              </p>
            )}
          </div>

          {/* Test API Call */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Test API Call
            </h2>
            <button
              onClick={async () => {
                const token = getAccessToken();
                if (!token) {
                  alert('No token found');
                  return;
                }

                try {
                  const res = await fetch('http://localhost:8000/auth/me', {
                    headers: {
                      'Authorization': `Bearer ${token}`
                    }
                  });

                  const data = await res.json();
                  console.log('Response:', res.status, data);

                  if (res.ok) {
                    alert(`Success! User: ${data.email}`);
                  } else {
                    alert(`Failed with ${res.status}: ${JSON.stringify(data)}`);
                  }
                } catch (e: any) {
                  alert(`Error: ${e.message}`);
                }
              }}
              className="btn-primary"
            >
              Test /auth/me Endpoint
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
