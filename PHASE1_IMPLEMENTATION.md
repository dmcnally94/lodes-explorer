# LODES Explorer - Phase 1 Implementation

## What's Been Set Up

### Backend Structure (FastAPI)
- **Database Models**: SQLAlchemy models for CBSA, BlockGroups, and WAC employment data
- **API Endpoints**:
  - `GET /api/cbsas` - List all CBSAs
  - `GET /api/cbsa/{cbsa_code}` - Get CBSA details
  - `GET /api/blockgroups/{cbsa_code}` - Get block groups with geometry (GeoJSON)
  - `GET /api/filters` - Get filter options
  - `POST /api/blockgroups/filtered` - Get filtered block groups

### Frontend
- Interactive map view using Leaflet.js
- CBSA selector dropdown
- Filter panel for employment code, age, earnings, education
- Choropleth visualization by total jobs
- Legend and popup details

### Data Loading
- CSV parser that extracts CBSA codes and block group geometries
- WAC data ingestion with all demographic/industry fields
- SQLite database (default, can switch to PostgreSQL)

## Next Steps for Phase 2

1. **Advanced Demographic Filters**
   - Race/Ethnicity (CR codes)
   - Sex (CS codes)
   - Firm size and age (CFS, CFA codes)

2. **Performance Optimization**
   - Database indexing for common queries
   - Tile-based rendering for large datasets
   - Query pagination

3. **UI Refinements**
   - Data-driven legend coloring
   - Drill-down capabilities
   - Export filtered data as CSV/GeoJSON

4. **Additional Visualizations**
   - Bar charts for industry breakdown
   - Time series analysis
   - Heatmaps for specific industries

## Getting Started

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Load data: `python load_data.py`
3. Run server: `python -m uvicorn backend.app:app --reload`
4. Open browser: `http://localhost:8000`
