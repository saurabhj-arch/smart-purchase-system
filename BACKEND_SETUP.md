# Backend Setup & Fix Guide

## Problem Summary
The scraping functionality was not working properly when users were logged in. This was caused by:

1. **Missing `_save_product_view` method** in `ProductPriceView` - causing AttributeError when trying to save recently viewed items
2. **Cache operation failures not being handled gracefully** - if the cache table didn't exist, the entire search could fail
3. **Missing Django cache table** - required for the cache-based optimization for logged-in users

## Setup Instructions

### 1. Initialize Django Cache Table
The project uses Django's database cache backend. You MUST create the cache table:

```bash
cd backend
python manage.py createcachetable
```

### 2. Run Migrations
Ensure all database migrations are applied:

```bash
python manage.py migrate
```

### 3. Load Initial Data
Load the required website fixtures (Amazon, Flipkart, Croma):

```bash
python manage.py loaddata products/fixtures/websites.json
```

### 4. Automated Setup
Alternatively, run the provided setup script:

```bash
cd backend
bash setup.sh
```

## Testing the Fix

### Test 1: Guest Search (Should work)
```bash
curl -X POST http://127.0.0.1:8000/api/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "iPhone"}'
```

### Test 2: Authenticated Search (Should now work)
```bash
# First, get a JWT token by logging in
export TOKEN=$(curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' | jq -r .access)

# Then search with the token
curl -X POST http://127.0.0.1:8000/api/search/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "iPhone"}'
```

### Test 3: Product Price View with Authenticated User
```bash
curl -X GET http://127.0.0.1:8000/api/search/product/1/ \
  -H "Authorization: Bearer $TOKEN"
```

### Test 4: Recently Viewed (Authenticated Users Only)
```bash
curl -X GET http://127.0.0.1:8000/api/accounts/recently-viewed/ \
  -H "Authorization: Bearer $TOKEN"
```

## What Was Fixed

### 1. ProductPriceView Missing Methods
**File**: `search/views.py`
- Added `_save_product_view()` method to ProductPriceView
- Added `_prune_recently_viewed()` method to ProductPriceView
- These methods now work independently for each view

### 2. Improved Cache Error Handling
**File**: `search/service.py`
- Added try/except blocks around cache.get() and cache.set()
- Cache failures no longer break the scraping functionality
- Scraping continues even if cache table doesn't exist
- Detailed error logging for debugging

### 3. Frontend API Utilities
**File**: `frontend/src/utils/api.js`
- Created centralized API utility functions
- Automatic JWT token injection in Authorization headers
- Consistent error handling across API calls

## How It Works Now

### For Guest Users (Anonymous)
1. Request comes in without authentication
2. Scraping service detects anonymous user
3. Always scrapes fresh, no caching
4. Returns results immediately
5. Recently viewed is NOT saved (no user association)

### For Logged-In Users
1. Request comes in with JWT token in Authorization header
2. Django REST Framework authenticates the user via JWT
3. Scraping service detects authenticated user
4. Checks cache using user ID and query
5. If cache hit: returns cached results immediately
6. If cache miss: scrapes fresh, stores in cache for 30 minutes
7. After search, top result is saved to recently viewed
8. When viewing product detail, product is saved to recently viewed
9. Recently viewed list is limited to 5 most recent items

## Database Schema

### RecentlyViewed Model
```python
class RecentlyViewed(models.Model):
    user = ForeignKey(User)        # Logged-in user
    product = ForeignKey(Product)  # Product viewed
    viewed_at = DateTimeField()    # When it was viewed
    
    unique_together = ('user', 'product')
```

## Performance Optimizations

1. **JWT Authentication**: Stateless authentication, no session lookups needed
2. **User-Specific Caching**: Results cached per user, enabling cache hits for repeated searches
3. **Cache Fallback**: If cache is unavailable, scraping still works
4. **Recently Viewed Capping**: Limited to 5 items to prevent database bloat

## Troubleshooting

### Issue: "No results found" for logged-in users
1. Check if cache table exists: `python manage.py shell`
   ```python
   from django.core.cache import cache
   cache.set('test', 'value', 60)
   print(cache.get('test'))  # Should print 'value'
   ```
2. If not working, run: `python manage.py createcachetable`

### Issue: JWT token not recognized
1. Verify token is sent in Authorization header: `Bearer {token}`
2. Check token expiration (default: 1 hour)
3. If expired, use refresh endpoint: `POST /api/accounts/token/refresh/`

### Issue: Recently viewed not saving
1. Ensure user is authenticated (check `request.user.is_authenticated`)
2. Check database for RecentlyViewed table: `python manage.py migrate`
3. Look for exceptions in console output

## Environment Configuration

### CORS
Frontend at `localhost:3000` can communicate with backend at `127.0.0.1:8000`

### Cache Backend
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
        "TIMEOUT": 1800,  # 30 minutes
    }
}
```

### JWT Configuration
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

## Next Steps

1. Run the setup script: `bash backend/setup.sh`
2. Start the backend: `python manage.py runserver`
3. Start the frontend: `cd frontend && npm start`
4. Test with both guest and logged-in users
5. Check console logs for cache hits/misses and recently viewed saves
