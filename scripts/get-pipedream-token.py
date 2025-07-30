#!/usr/bin/env python3
"""
Pipedream OAuth Token Fetcher

This script fetches an access token from Pipedream using OAuth client credentials.
Based on: https://pipedream.com/docs/rest-api/auth

Usage:
    python scripts/get-pipedream-token.py

Environment variables needed:
    PIPEDREAM_CLIENT_ID=your_client_id
    PIPEDREAM_CLIENT_SECRET=your_client_secret
    PIPEDREAM_WORKSPACE_ID=your_workspace_id (optional, for reference)
"""

import os
import requests
import json
from datetime import datetime, timedelta

# Import the environment loader utility
from env_loader import load_env_from_base, get_env_var


def get_pipedream_token():
    """Fetch access token from Pipedream using OAuth client credentials."""

    # Get credentials from environment variables
    client_id = get_env_var("PIPEDREAM_CLIENT_ID")
    client_secret = get_env_var("PIPEDREAM_CLIENT_SECRET")
    workspace_id = get_env_var("PIPEDREAM_WORKSPACE_ID")

    if not client_id or not client_secret:
        print("❌ Error: Missing required environment variables")
        print("Please set the following environment variables:")
        print("  PIPEDREAM_CLIENT_ID=your_client_id")
        print("  PIPEDREAM_CLIENT_SECRET=your_client_secret")
        print("  PIPEDREAM_WORKSPACE_ID=your_workspace_id (optional)")
        return None

    # OAuth token endpoint
    token_url = "https://api.pipedream.com/v1/oauth/token"

    # Request payload for client credentials grant
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    headers = {"Content-Type": "application/json"}

    try:
        print("🔄 Fetching Pipedream access token...")
        response = requests.post(token_url, json=payload, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour

            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=expires_in)

            print("✅ Successfully obtained Pipedream access token!")
            print(f"📅 Token expires at: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(
                f"⏱️  Valid for: {expires_in} seconds ({expires_in // 3600}h {expires_in % 3600 // 60}m)"
            )

            if workspace_id:
                print(f"🏢 Workspace ID: {workspace_id}")

            print("\n🔑 Access Token:")
            print(f"Bearer {access_token}")

            # Save token to file for easy use
            token_info = {
                "access_token": access_token,
                "expires_at": expires_at.isoformat(),
                "expires_in": expires_in,
                "workspace_id": workspace_id,
                "fetched_at": datetime.now().isoformat(),
            }

            with open("pipedream_token.json", "w") as f:
                json.dump(token_info, f, indent=2)

            print("\n💾 Token saved to: pipedream_token.json")
            print("\n📋 Usage examples:")
            print("  # Set as environment variable:")
            print(f"  export PIPEDREAM_API_KEY='{access_token}'")
            print("\n  # Use in curl:")
            print(
                f"  curl -H 'Authorization: Bearer {access_token}' https://api.pipedream.com/v1/users/me"
            )

            return access_token

        else:
            print(f"❌ Error: Failed to get token (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_token(access_token):
    """Test the access token by making a simple API call."""
    if not access_token:
        return False

    try:
        print("\n🧪 Testing access token...")
        response = requests.get(
            "https://api.pipedream.com/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token is valid!")
            print(f"👤 Authenticated as: {user_data.get('email', 'Unknown')}")
            return True
        else:
            print(f"❌ Token test failed (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Pipedream OAuth Token Fetcher")
    print("=" * 40)
    
    # Load environment variables from .env file
    load_env_from_base()
    print()

    # Fetch the token
    token = get_pipedream_token()

    if token:
        # Test the token
        test_token(token)

        print("\n" + "=" * 40)
        print("✨ Done! You can now use the access token with Pipedream API calls.")
        print(
            "💡 Remember: Access tokens expire after 1 hour and need to be refreshed."
        )
    else:
        print("\n❌ Failed to obtain access token. Please check your credentials.")
