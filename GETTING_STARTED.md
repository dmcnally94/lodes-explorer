# Getting Started with LODES Explorer

## Installation

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Load Data (First Time Only)
The data loading script converts CSV files into a SQLite database:
```bash
python load_data.py .
```

This will:
- Create `lodes.db` with 3 tables (cbsas, blockgroups, wac_data)
- Load 15,785 employment records
- Parse WKT geometries
- Calculate CBSA totals

**Output:**
```
Loading data from: .
Creating database...
✓ Database tables created
Initializing CBSAs...
✓ CBSAs initialized
Loading block group geometries...
  Loading geometries from 31080_blockgroups2023.csv
    ✓ Loaded 8714 geometries for CBSA 31080
  Loading geometries from 47900_blockgroups2023.csv
    ✓ Loaded 4096 geometries for CBSA 47900
Loading WAC employment data...
  Loading WAC data from 31080_all2023.csv
    ✓ Loaded 8631 WAC records for CBSA 31080
  Loading WAC data from 41860_all2023.csv
    ✓ Loaded 3196 WAC records for CBSA 41860
  Loading WAC data from 47900_all2023.csv
    ✓ Loaded 3958 WAC records for CBSA 47900
✓ Data loading complete!
```

### 3. Start the Server

**Development Mode (with auto-reload):**
```bash
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Wait for:
```
Uvicorn running on http://0.0.0.0:8000
```

### 4. Open in Browser
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API Explorer**: http://localhost:8000/redoc

## Using the Application

### 1. Select a CBSA
Click the dropdown and choose from:
- **31080** - Los Angeles-Long Beach-Anaheim, CA (6.5M jobs)
- **41860** - San Francisco-Oakland-Fremont, CA (2.5M jobs)
- **47900** - Washington-Arlington-Alexandria, DC-VA-MD-WV (3.1M jobs)

### 2. View Block Groups
Map shows all block groups as colored regions:
- **Light yellow**: 0-100 jobs
- **Light green**: 100-500 jobs
- **Dark green**: 500-1,000 jobs
- **Very dark green**: 1,000+ jobs

### 3. Apply Filters
Choose filters and click "Apply":
- **Employment Sector**: Specific NAICS sector
- **Worker Age**: Age group range
- **Earnings Bracket**: Monthly wage range
- **Education Level**: Educational attainment

### 4. Explore Results
- Hover over block groups to see details
- Click for popup with statistics
- Color intensity shows metric concentration

## API Usage

### Get all CBSAs
```bash
curl http://localhost:8000/api/cbsas
```

Response:
```json
[
  {
    "id": 1,
    "cbsa_code": "31080",
    "cbsa_name": "Los Angeles-Long Beach-Anaheim, CA",
    "total_jobs": 6588635
  },
  ...
]
```

### Get block groups for a CBSA
```bash
curl http://localhost:8000/api/blockgroups/31080
```

Returns GeoJSON FeatureCollection with geometry and properties.

### Get filter options
```bash
curl http://localhost:8000/api/filters
```

Returns available employment codes, age groups, earnings brackets, and education levels.

### Filter by employment sector
```bash
curl -X POST "http://localhost:8000/api/blockgroups/filtered?cbsa_code=31080&employment_code=CNS09"
```

Filters block groups where Information sector has jobs.

## Troubleshooting

### Issue: "lodes.db not found"
**Solution**: Run `python load_data.py .` in the project root

### Issue: Port 8000 already in use
**Solution**: Kill the existing process and restart
```bash
# Windows PowerShell
Get-NetTCPConnection -LocalPort 8000 | Stop-Process

# Or use different port
python -m uvicorn backend.app:app --port 8001
```

### Issue: Geometry not showing on map
**Solution**: 
1. Check browser console (F12) for errors
2. Verify database has geometries: `sqlite3 lodes.db "SELECT COUNT(*) FROM blockgroups;"`
3. Check network tab - verify API calls are succeeding

### Issue: Slow response times
**Solution**: 
1. Confirm `lodes.db` is in the same directory as `load_data.py`
2. For filtering, multiple filters are AND-ed (more restrictive)
3. Washington DC (47900) is smaller - try that first

## Development Commands

### Check database contents
```bash
sqlite3 lodes.db
> SELECT * FROM cbsas;
> SELECT COUNT(*) FROM blockgroups;
> SELECT COUNT(*) FROM wac_data;
```

### Test API endpoint
```bash
python test_api.py
```

### View API documentation in browser
Open: http://localhost:8000/docs

### Run with debug logging
```bash
python -m uvicorn backend.app:app --reload --log-level debug
```

## File Manifest

| File | Purpose |
|------|---------|
| `load_data.py` | Load CSV → SQLite |
| `backend/app.py` | FastAPI application |
| `backend/routes/cbsa.py` | API endpoints |
| `frontend/index.html` | Web UI |
| `frontend/js/app.js` | Frontend logic |
| `frontend/js/map.js` | Leaflet map |
| `frontend/js/api.js` | API client |
| `frontend/css/style.css` | Styling |
| `lodes.db` | SQLite database (generated) |

## Performance Characteristics

- **Startup time**: ~2 seconds
- **CBSA load time**: <100ms
- **Block group rendering**: ~1 second (8,700 features)
- **Filtered query**: <50ms
- **Database size**: ~5 MB

## Architecture Decisions

### SQLite (not PostgreSQL)
- ✅ No external dependencies
- ✅ Single file database
- ✅ Good for <100M records
- ✅ No network overhead

### Vanilla JavaScript (not React)
- ✅ No build step required
- ✅ Lightweight
- ✅ Direct DOM manipulation
- ✅ Easier to debug

### Leaflet.js (not Mapbox)
- ✅ No API key required
- ✅ Open source
- ✅ Fast rendering
- ✅ Good for GeoJSON

## Next Steps

### To Extend the Application
1. Add more filters (race, firm size)
2. Create dashboard with charts
3. Export filtered data as CSV
4. Compare multiple CBSAs
5. Add time-series analysis

### To Optimize Performance
1. Add database indexes on common filter columns
2. Implement tile-based mapping for huge datasets
3. Add caching layer for popular queries
4. Use TileJSON format for complex geometries

---

**Happy exploring!** 🗺️📊

For issues or questions, check the main README.md or inspect browser console for errors.
