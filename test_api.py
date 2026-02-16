import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:8000/api/blockgroups/31080')
    data = json.loads(response.read().decode())
    print(f"✓ Loaded {len(data['features'])} block groups for Los Angeles")
    print(f"✓ Sample block group: {data['features'][0]['properties']['bg_geoid']}")
    print(f"✓ Jobs in first block group: {data['features'][0]['properties']['total_jobs']:,}")
    print(f"✓ Geometry type: {data['features'][0]['geometry']['type']}")
except Exception as e:
    print(f"Error: {e}")
