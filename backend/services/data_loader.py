import os
import json
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database.models import CBSA, BlockGroup, WACData


CBSA_MAPPING = {
    "31080": "Los Angeles-Long Beach-Anaheim, CA",
    "41860": "San Francisco-Oakland-Fremont, CA",
    "47900": "Washington-Arlington-Alexandria, DC-VA-MD-WV",
}

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


def extract_cbsa_from_geoid(geoid: str) -> str:
    """Extract CBSA code from block group GEOID (first 5 digits after state/county)"""
    if len(geoid) >= 5:
        return geoid[:5]
    return None


def load_blockgroup_geometries(db: Session, data_dir: str = "."):
    """Load block group geometries from CSV files"""
    for cbsa_code in CBSA_MAPPING.keys():
        bg_file = Path(data_dir) / f"{cbsa_code}_blockgroups2023.csv"
        
        if not bg_file.exists():
            print(f"Skipping {bg_file} - file not found")
            continue
        
        print(f"Loading geometries from {bg_file}")
        df = pd.read_csv(bg_file)
        
        for _, row in df.iterrows():
            bg_geoid = str(row["bgrp"]).strip()
            geometry = str(row["geometry"]).strip()
            
            db_bg = BlockGroup(
                cbsa_code=cbsa_code,
                bg_geoid=bg_geoid,
                geometry=geometry,
            )
            
            try:
                db.add(db_bg)
                db.commit()
            except IntegrityError:
                db.rollback()
                continue
        
        print(f"Loaded geometries for CBSA {cbsa_code}")


def load_wac_data(db: Session, data_dir: str = "."):
    """Load WAC employment data from CSV files"""
    wac_columns = [
        "c000", "ca01", "ca02", "ca03", "ce01", "ce02", "ce03",
        "cns01", "cns02", "cns03", "cns04", "cns05", "cns06", "cns07", 
        "cns08", "cns09", "cns10", "cns11", "cns12", "cns13", "cns14", 
        "cns15", "cns16", "cns17", "cns18", "cns19", "cns20",
        "cr01", "cr02", "cr03", "cr04", "cr05", "cr07",
        "ct01", "ct02",
        "cd01", "cd02", "cd03", "cd04",
        "cs01", "cs02",
        "cfa01", "cfa02", "cfa03", "cfa04", "cfa05",
        "cfs01", "cfs02", "cfs03", "cfs04", "cfs05",
    ]
    
    for cbsa_code in CBSA_MAPPING.keys():
        wac_file = Path(data_dir) / f"{cbsa_code}_blockgroups2023.csv"
        
        if not wac_file.exists():
            print(f"Skipping {wac_file} - file not found")
            continue
        
        print(f"Loading WAC data from {wac_file}")
        df = pd.read_csv(wac_file)
        
        # Map w_geocode to block group GEOID
        if "w_geocode" in df.columns:
            df["bg_geoid"] = df["w_geocode"].astype(str).str[:12]
        else:
            print(f"Warning: w_geocode column not found in {wac_file}")
            continue
        
        total_jobs_cbsa = 0
        
        for _, row in df.iterrows():
            try:
                bg_geoid = str(row["bg_geoid"]).strip()
                
                wac_data = WACData(
                    cbsa_code=cbsa_code,
                    bg_geoid=bg_geoid,
                )
                
                # Populate all WAC columns
                for col in wac_columns:
                    if col in row and pd.notna(row[col]):
                        try:
                            setattr(wac_data, col, int(row[col]))
                        except (ValueError, TypeError):
                            setattr(wac_data, col, 0)
                
                db.add(wac_data)
                total_jobs_cbsa += wac_data.c000
                
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        db.commit()
        
        # Update CBSA total jobs
        cbsa = db.query(CBSA).filter(CBSA.cbsa_code == cbsa_code).first()
        if cbsa:
            cbsa.total_jobs = total_jobs_cbsa
            db.commit()
        
        print(f"Loaded {len(df)} WAC records for CBSA {cbsa_code}")


def initialize_cbsas(db: Session):
    """Initialize CBSA records"""
    for code, name in CBSA_MAPPING.items():
        existing = db.query(CBSA).filter(CBSA.cbsa_code == code).first()
        if not existing:
            cbsa = CBSA(cbsa_code=code, cbsa_name=name)
            db.add(cbsa)
            db.commit()
            print(f"Created CBSA {code}: {name}")
        else:
            # Update name if it differs from mapping
            if existing.cbsa_name != name:
                existing.cbsa_name = name
                db.commit()
                print(f"Updated CBSA {code} name to: {name}")
            else:
                print(f"CBSA {code} already exists")


def load_all_data(db: Session, data_dir: str = "."):
    """Load all data in proper sequence"""
    print("Initializing CBSAs...")
    initialize_cbsas(db)
    
    print("Loading block group geometries...")
    load_blockgroup_geometries(db, data_dir)
    
    print("Loading WAC employment data...")
    load_wac_data(db, data_dir)
    
    print("Data loading complete!")
