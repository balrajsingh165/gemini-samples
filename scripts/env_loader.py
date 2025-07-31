#!/usr/bin/env python3
"""
Environment Loader Utility

This module provides a function to load environment variables from a .env file
in the project root directory. All scripts can import this to ensure they
load environment variables from the correct location.

Usage:
    from env_loader import load_env_from_base
    load_env_from_base()
"""

import os
from pathlib import Path


def load_env_from_base():
    """
    Load environment variables from .env file in the project root directory.

    This function looks for a .env file in the parent directory of the scripts folder
    and loads all environment variables from it.
    """
    # Get the project root directory (parent of scripts folder)
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"

    if env_file.exists():
        print(f"📁 Loading environment from: {env_file}")
        loaded_vars = []

        with open(env_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse key=value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]

                    # Set environment variable
                    os.environ[key] = value
                    loaded_vars.append(key)

        # if loaded_vars:
        #     print(f"✅ Loaded {len(loaded_vars)} environment variables: {', '.join(loaded_vars)}")
        # else:
        #     print("⚠️  No environment variables found in .env file")
    else:
        print(f"⚠️  No .env file found at: {env_file}")
        print("   Make sure you have created a .env file in the project root directory")
        print("   You can copy env.sample to .env and fill in your API keys")


def get_env_var(key, default=None, required=False):
    """
    Get an environment variable with optional validation.

    Args:
        key (str): The environment variable name
        default: Default value if not found
        required (bool): If True, raises an error if the variable is not set

    Returns:
        The environment variable value or default

    Raises:
        ValueError: If required=True and the variable is not set
    """
    value = os.getenv(key, default)

    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")

    return value


if __name__ == "__main__":
    # Test the environment loader
    print("🧪 Testing Environment Loader")
    print("=" * 40)
    load_env_from_base()

    # Test getting some common variables
    print("\n🔍 Testing environment variables:")
    test_vars = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "PIPEDREAM_CLIENT_ID"]

    for var in test_vars:
        value = get_env_var(var)
        if value:
            # Show first few characters for security
            display_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  {var}: {display_value}")
        else:
            print(f"  {var}: Not set")
