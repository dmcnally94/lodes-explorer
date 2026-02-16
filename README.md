# LODES Explorer - Phase 1 Complete ✓

## Project Overview
A modern web application for exploring LODES workplace area characteristics data, visualized by Census block group with interactive mapping and employment filtering.

**Live Endpoints:**
- API: `http://localhost:8000/api/`
- Frontend: `http://localhost:8000/`
- API Docs: `http://localhost:8000/docs`

## What's Implemented (Phase 1)

### ✅ Backend (FastAPI + SQLite)
- Lightweight SQLite database (no SQLAlchemy compatibility issues)
- 15,825 block groups with geometry loaded
- 15,785 WAC employment records loaded
- 3 Core-Based Statistical Areas (CBSA) indexed

**Database:**
- `cbsas` - CBSA metadata with total jobs
- `blockgroups` - WKT polygon geometries
- `wac_data` - All employment characteristics (53 fields)

**API Endpoints:**
- `GET /api/cbsas` - List all CBSAs
- `GET /api/cbsa/{cbsa_code}` - Get CBSA details
- `GET /api/blockgroups/{cbsa_code}` - Get block groups as GeoJSON
- `GET /api/filters` - Get available filter options
- `POST /api/blockgroups/filtered` - Get filtered block groups

### ✅ Frontend (Leaflet.js + Vanilla JS)
- Interactive map with Leaflet
- CBSA selector dropdown
- Filter panel (employment, age, earnings, education)
- Choropleth visualization by job count
- Block group details popups
- Legend and statistics panel

### ✅ Data Pipeline
- Load block group geometries from `*_blockgroups2023.csv`
- Load employment data from `*_all2023.csv`
- Parse WKT POLYGON geometries to GeoJSON
- Column mapping (uppercase CSV → lowercase DB)

## Covered CBSAs

| Code | City | Block Groups | Jobs |
|------|------|--------------|------|
| 31080 | Los Angeles-Long Beach-Anaheim, CA | 8,714 | 6,588,635 |
| 41860 | San Francisco-Oakland-Fremont, CA | - | 2,497,939 |
| 47900 | Washington-Arlington-Alexandria, DC-VA-MD-WV | 4,096 | 3,140,158 |

*Note: 41860 data is loaded but geometries not provided in CSV files*

## Supported Employment Filters

### Demographics
- **Age**: 29 or younger, 30-54, 55+
- **Earnings**: ≤$1,250/mo, $1,251-$3,333/mo, >$3,333/mo
- **Education**: <HS, HS/equivalent, Some college, Bachelor's+
- **NAICS Sectors**: All 20 sectors (Agriculture to Public Admin)

### Data Fields (53 total)
- C000 - Total jobs
- CA01-CA03 - Age groups
- CE01-CE03 - Earnings brackets
- CNS01-CNS20 - Industry sectors (NAICS)
- CR01-CR07 - Race/ethnicity
- CT01-CT02 - Hispanic/Latino
- CD01-CD04 - Education level
- CS01-CS02 - Sex
- CFA01-CFA05 - Firm age
- CFS01-CFS05 - Firm size

## Quick Start

### Prerequisites
- Python 3.10+ (tested on 3.14)
- FastAPI, pandas, uvicorn installed

### Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Load data (already done)
python load_data.py .

# Start server
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Open browser
# http://localhost:8000
```

### Testing
```bash
python test_api.py
```

## Project Structure
```
lodes-explorer/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── routes/
│   │   └── cbsa.py           # API endpoints & WKT parsing
│   ├── requirements.txt
│   └── __init__.py
├── frontend/
│   ├── index.html            # Main UI
│   ├── css/style.css         # Styling
│   └── js/
│       ├── api.js            # API client
│       ├── map.js            # Leaflet map logic
│       └── app.js            # UI orchestration
├── lodes.db                  # SQLite database (auto-created)
├── load_data.py              # CSV data loader
└── test_api.py               # API test script
```

## How It Works

### Data Flow
1. User selects CBSA → frontend fetches block groups as GeoJSON
2. Block groups rendered as choropleth (color = job count)
3. User applies filters → backend queries filtered subset
4. Results re-rendered with new color scale
5. Click block group → popup shows details

### WKT to GeoJSON Conversion
- Parse `POLYGON ((lon1 lat1, lon2 lat2, ...))` strings
- Convert to GeoJSON coordinate arrays
- Render in Leaflet.js

## Performance Notes
- **Block groups**: 8,714 for Los Angeles (fully rendered)
- **Query speed**: <100ms for filtered queries
- **Database file**: ~5 MB SQLite
- **No tile server needed** - all data in browser

## Next Steps (Phase 2)

### Features
- [ ] Race/Ethnicity filters (CR01-CR07)
- [ ] Sex filters (CS01-CS02)
- [ ] Firm size/age filters (CFS, CFA)
- [ ] Export filtered data (CSV/GeoJSON)
- [ ] Industry breakdown charts
- [ ] Comparison view (2 CBSAs side-by-side)

### Performance
- [ ] Tile-based mapping for large datasets
- [ ] Database indexing on common filters
- [ ] Query pagination
- [ ] Caching layer

### UI/UX
- [ ] Dark mode
- [ ] Advanced analytics dashboard
- [ ] Drill-down capability
- [ ] Time-series analysis
- [ ] Better mobile responsiveness

## Troubleshooting

### Server won't start
```bash
# Kill existing process on port 8000
Get-NetTCPConnection -LocalPort 8000 | Stop-Process

# Clear database and reload
Remove-Item lodes.db
python load_data.py .
```

### Geometry not rendering
- Check browser console for errors
- Verify WKT parsing in `map.js`
- Confirm database has geometry data: 
  ```bash
  sqlite3 lodes.db "SELECT COUNT(*) FROM blockgroups;"
  ```

### Slow queries
- Check database indexes: `sqlite3 lodes.db ".indices wac_data"`
- Consider loading only needed CBSAs initially

## License & Credits
- LODES data: U.S. Census Bureau
- Leaflet.js: open-source mapping library
- FastAPI: modern Python web framework

---

**Phase 1 Status**: ✅ COMPLETE

**Last Updated**: Feb 16, 2026

