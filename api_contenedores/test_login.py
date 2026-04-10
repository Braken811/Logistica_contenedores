#!/usr/bin/env python
"""Test script para diagnosticar error en login"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Intentar login
print("=" * 60)
print("🔐 Intentando hacer login...")
print("=" * 60)

login_data = {
    "user": "admin",
    "password": "admin123"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        timeout=5
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nResponse Body:\n{json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
