#!/usr/bin/env python3
"""
Test script to verify environment loading works correctly.
"""

from env_loader import load_env_from_base, get_env_var

def test_env_loading():
    print("🧪 Testing Environment Loading")
    print("=" * 40)
    
    # Load environment variables
    load_env_from_base()
    
    # Test getting some variables
    print("\n🔍 Testing environment variables:")
    
    test_vars = [
        ("GEMINI_API_KEY", "Required for Gemini API"),
        ("GOOGLE_API_KEY", "Alternative name for Gemini API key"),
        ("PIPEDREAM_CLIENT_ID", "Optional - for Pipedream OAuth"),
        ("PIPEDREAM_CLIENT_SECRET", "Optional - for Pipedream OAuth"),
        ("PIPEDREAM_WORKSPACE_ID", "Optional - for Pipedream workspace reference")
    ]
    
    for var_name, description in test_vars:
        value = get_env_var(var_name)
        if value:
            # Show first few characters for security
            display_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✅ {var_name}: {display_value}")
        else:
            print(f"  ⚠️  {var_name}: Not set ({description})")
    
    print("\n✨ Environment loading test completed!")

if __name__ == "__main__":
    test_env_loading() 