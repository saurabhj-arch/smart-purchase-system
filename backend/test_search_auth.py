"""
Test script to diagnose scraping issues with authenticated users.
Run: python manage.py shell < test_search_auth.py
"""
from django.contrib.auth.models import User
from django.test import Client
import json

# Create a test user
user = User.objects.filter(username='testuser').first()
if not user:
    user = User.objects.create_user(username='testuser', password='testpass123')
    print(f"✓ Created test user: {user.username}")
else:
    print(f"✓ Using existing test user: {user.username}")

# Test 1: Check if we can get a token for the user
print("\n=== Test 1: JWT Token Generation ===")
from rest_framework_simplejwt.tokens import RefreshToken
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"✓ Generated access token (first 20 chars): {access_token[:20]}...")

# Test 2: Guest search (should work)
print("\n=== Test 2: Guest Search ===")
client = Client()
response = client.post(
    '/api/search/',
    json.dumps({'query': 'iPhone'}),
    content_type='application/json'
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Guest search returned {len(data)} products")
else:
    print(f"✗ Error: {response.json()}")

# Test  3: Authenticated search (this is where issues might occur)
print("\n=== Test 3: Authenticated Search ===")
client = Client()
headers = {
    'HTTP_AUTHORIZATION': f'Bearer {access_token}',
    'CONTENT_TYPE': 'application/json'
}
response = client.post(
    '/api/search/',
    json.dumps({'query': 'iPhone'}),
    content_type='application/json',
    **{k.replace('HTTP_', ''): v for k, v in headers.items() if k.startswith('HTTP_')}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✓ Authenticated search returned {len(data)} products")
else:
    print(f"✗ Error: {response.json()}")

# Test 4: Check request.user in middleware
print("\n=== Test 4: Check User Authentication in View ===")
from rest_framework.test import APIClient
api_client = APIClient()
# Without token
response = api_client.post('/api/search/', {'query': 'iPhone'})
print(f"Without token - Status: {response.status_code}")

# With token
api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
response = api_client.post('/api/search/', {'query': 'iPhone'})
print(f"With token - Status: {response.status_code}")
if response.status_code == 200:
    print(f"✓ Authenticated search returned {len(response.json())} products")
else:
    print(f"✗ Error: {response.json()}")

# Test 5: Check cache directly
print("\n=== Test 5: Cache Operations ===")
from django.core.cache import cache
from search.service import get_cache_key

test_key = get_cache_key(user.id, 'iPhone')
print(f"Cache key for user {user.id}: {test_key}")

# Try to get/set cache
cache.set(test_key, {'test': 'data'}, 300)
cached = cache.get(test_key)
if cached:
    print(f"✓ Cache set/get works: {cached}")
else:
    print(f"✗ Cache not working properly")

print("\n=== All Tests Complete ===")
