import urllib.request
import json

print("Testing LODES Explorer API Endpoints\n" + "=" * 50)

try:
    # Test 1: Health check
    response = urllib.request.urlopen('http://localhost:8000/health')
    print("✓ Health check: OK")
    
    # Test 2: CBSAs
    response = urllib.request.urlopen('http://localhost:8000/api/cbsas')
    cbsas = json.loads(response.read().decode())
    print(f"✓ CBSAs loaded: {len(cbsas)} areas")
    
    # Test 3: Block groups
    response = urllib.request.urlopen('http://localhost:8000/api/blockgroups/31080')
    bg_data = json.loads(response.read().decode())
    print(f"✓ Block groups (31080): {len(bg_data['features'])} features")
    
    # Test 4: Filters
    response = urllib.request.urlopen('http://localhost:8000/api/filters')
    filters = json.loads(response.read().decode())
    print(f"✓ Filter options:")
    print(f"  - Employment codes: {len(filters['employment_codes'])} sectors")
    print(f"  - Age groups: {len(filters['age_groups'])} groups")
    print(f"  - Earnings brackets: {len(filters['earnings_brackets'])} brackets")
    print(f"  - Education levels: {len(filters['education_levels'])} levels")
    
    print("\n✅ All API endpoints are working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure the server is running:")
    print("  python -m uvicorn backend.app:app --reload")
