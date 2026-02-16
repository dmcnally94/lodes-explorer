import sqlite3
import json
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["CBSA"])

DB_FILE = "lodes.db"

NAICS_DESCRIPTIONS = {
    "CNS01": "Agriculture, Forestry, Fishing and Hunting",
    "CNS02": "Mining, Quarrying, and Oil and Gas Extraction",
    "CNS03": "Utilities",
    "CNS04": "Construction",
    "CNS05": "Manufacturing",
    "CNS06": "Wholesale Trade",
    "CNS07": "Retail Trade",
    "CNS08": "Transportation and Warehousing",
    "CNS09": "Information",
    "CNS10": "Finance and Insurance",
    "CNS11": "Real Estate and Rental and Leasing",
    "CNS12": "Professional, Scientific, and Technical Services",
    "CNS13": "Management of Companies and Enterprises",
    "CNS14": "Administrative and Support Services",
    "CNS15": "Educational Services",
    "CNS16": "Health Care and Social Assistance",
    "CNS17": "Arts, Entertainment, and Recreation",
    "CNS18": "Accommodation and Food Services",
    "CNS19": "Other Services",
    "CNS20": "Public Administration",
}


class CBSAResponse(BaseModel):
    id: int
    cbsa_code: str
    cbsa_name: str
    total_jobs: int


class FilterOptions(BaseModel):
    employment_codes: List[dict]
    age_groups: List[dict]
    earnings_brackets: List[dict]
    education_levels: List[dict]


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/cbsas", response_model=List[CBSAResponse])
def list_cbsas():
    """Get all available CBSAs"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, cbsa_code, cbsa_name, total_jobs FROM cbsas ORDER BY cbsa_code")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


@router.get("/cbsa/{cbsa_code}", response_model=CBSAResponse)
def get_cbsa(cbsa_code: str):
    """Get details for a specific CBSA"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, cbsa_code, cbsa_name, total_jobs FROM cbsas WHERE cbsa_code = ?", (cbsa_code,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="CBSA not found")
    
    return dict(row)


@router.post("/blockgroups/filtered")
@router.get("/blockgroups/filtered")
def get_filtered_blockgroups(
    cbsa_code: str,
    employment_code: Optional[str] = None,
    age_group: Optional[str] = None,
    earnings_bracket: Optional[str] = None,
    education_level: Optional[str] = None,
):
    """
    Get block groups filtered by employment characteristics.
    Returns GeoJSON FeatureCollection with filtered data.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Build query
    query = """
        SELECT bg.bg_geoid, bg.geometry, w.*
        FROM blockgroups bg
        JOIN wac_data w ON bg.bg_geoid = w.bg_geoid AND bg.cbsa_code = w.cbsa_code
        WHERE bg.cbsa_code = ?
    """
    params = [cbsa_code]
    
    # Add employment code filter
    if employment_code:
        col_name = employment_code.lower()
        query += f" AND w.{col_name} > 0"
    
    # Add age group filter
    if age_group:
        col_name = age_group.lower()
        query += f" AND w.{col_name} > 0"
    
    # Add earnings bracket filter
    if earnings_bracket:
        col_name = earnings_bracket.lower()
        query += f" AND w.{col_name} > 0"
    
    # Add education level filter
    if education_level:
        col_name = education_level.lower()
        query += f" AND w.{col_name} > 0"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    features = []
    for row in rows:
        try:
            geometry = parse_polygon_wkt(row["geometry"])
            if not geometry:
                continue

            # Compute metric_value as the combination of all selected filters.
            # Since the WAC data provides marginal counts (no cross-tab),
            # we conservatively approximate the intersection by taking the minimum
            # of the selected filter columns for this block group.
            selected_cols = []
            if employment_code:
                selected_cols.append(employment_code.lower())
            if age_group:
                selected_cols.append(age_group.lower())
            if earnings_bracket:
                selected_cols.append(earnings_bracket.lower())
            if education_level:
                selected_cols.append(education_level.lower())

            metric_value = row["c000"] or 0
            if selected_cols:
                vals = []
                keys = set(row.keys())
                for col in selected_cols:
                    try:
                        vals.append(row[col] if col in keys and row[col] is not None else 0)
                    except Exception:
                        vals.append(0)
                metric_value = int(min(vals)) if vals else 0

            properties = {
                "bg_geoid": row["bg_geoid"],
                "metric_value": metric_value or 0,
                "total_jobs": row["c000"] or 0,
                "filter_employment_code": employment_code or None,
                "active_filters": selected_cols,
            }

            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": geometry
            }
            features.append(feature)
        except Exception as e:
            print(f"Error processing row: {e}")
            continue

    return {
        "type": "FeatureCollection",
        "features": features
    }



@router.get("/blockgroups/{cbsa_code}")
def get_blockgroups(cbsa_code: str):
    """
    Get all block groups for a CBSA with geometry and aggregated statistics.
    Returns GeoJSON FeatureCollection.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get block groups
    cursor.execute("""
        SELECT bg.id, bg.cbsa_code, bg.bg_geoid, bg.geometry,
               w.c000, w.ca01, w.ca02, w.ca03, w.ce01, w.ce02, w.ce03
        FROM blockgroups bg
        LEFT JOIN wac_data w ON bg.bg_geoid = w.bg_geoid AND bg.cbsa_code = w.cbsa_code
        WHERE bg.cbsa_code = ?
    """, (cbsa_code,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        # Return an empty FeatureCollection when a CBSA exists but has no block groups
        # (avoid returning 404 which makes the frontend harder to handle)
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    features = []
    for row in rows:
        try:
            # Parse WKT polygon to GeoJSON coordinates
            geometry = parse_polygon_wkt(row["geometry"])
            if not geometry:
                continue
            
            properties = {
                "bg_geoid": row["bg_geoid"],
                "total_jobs": row["c000"] or 0,
                "ca01": row["ca01"] or 0,
                "ca02": row["ca02"] or 0,
                "ca03": row["ca03"] or 0,
                "ce01": row["ce01"] or 0,
                "ce02": row["ce02"] or 0,
                "ce03": row["ce03"] or 0,
            }
            
            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": geometry
            }
            features.append(feature)
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/filters")
def get_filter_options():
    """Get available filter options"""
    return FilterOptions(
        employment_codes=[
            {"code": code, "name": desc}
            for code, desc in NAICS_DESCRIPTIONS.items()
        ],
        age_groups=[
            {"code": "CA01", "name": "29 or younger"},
            {"code": "CA02", "name": "30 to 54"},
            {"code": "CA03", "name": "55 or older"},
        ],
        earnings_brackets=[
            {"code": "CE01", "name": "$1,250/month or less"},
            {"code": "CE02", "name": "$1,251-$3,333/month"},
            {"code": "CE03", "name": ">$3,333/month"},
        ],
        education_levels=[
            {"code": "CD01", "name": "Less than high school"},
            {"code": "CD02", "name": "High school or equivalent"},
            {"code": "CD03", "name": "Some college or Associate degree"},
            {"code": "CD04", "name": "Bachelor's or advanced degree"},
        ]
    )



def parse_polygon_wkt(wkt_string: str) -> dict:
    """Parse WKT polygon string to GeoJSON geometry"""
    try:
        # Remove 'POLYGON ((' and trailing '))'
        wkt_string = wkt_string.strip()
        if not wkt_string.startswith("POLYGON"):
            return None
        
        # Extract coordinates
        start = wkt_string.find("((") + 2
        end = wkt_string.rfind("))")
        coords_str = wkt_string[start:end]
        
        # Parse coordinate pairs
        coords = []
        for pair in coords_str.split(","):
            parts = pair.strip().split()
            if len(parts) >= 2:
                try:
                    lon, lat = float(parts[0]), float(parts[1])
                    coords.append([lon, lat])
                except:
                    continue
        
        if len(coords) < 3:
            return None
        
        return {
            "type": "Polygon",
            "coordinates": [coords]
        }
    except Exception as e:
        print(f"Error parsing WKT: {e}")
        return None
