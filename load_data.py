#!/usr/bin/env python3
"""
Data loading script for LODES Explorer
Run this to populate the database with CSV data
"""

import sys
import json
import pandas as pd
import sqlite3
from pathlib import Path

# Database connection
DB_FILE = "lodes.db"

CBSA_MAPPING = {
    "31080": "Los Angeles-Long Beach-Anaheim, CA",
    "41860": "Portland-Vancouver-Hillsboro, OR-WA",
    "47900": "Seattle-Tacoma-Bellevue, WA",
}

def init_database():
    """Create database tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # CBSA table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cbsas (
            id INTEGER PRIMARY KEY,
            cbsa_code TEXT UNIQUE NOT NULL,
            cbsa_name TEXT NOT NULL,
            total_jobs INTEGER DEFAULT 0
        )
    """)
    
    # BlockGroups table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockgroups (
            id INTEGER PRIMARY KEY,
            cbsa_code TEXT NOT NULL,
            bg_geoid TEXT NOT NULL,
            geometry TEXT NOT NULL,
            UNIQUE(cbsa_code, bg_geoid)
        )
    """)
    
    # WAC Data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wac_data (
            id INTEGER PRIMARY KEY,
            cbsa_code TEXT NOT NULL,
            bg_geoid TEXT NOT NULL,
            c000 INTEGER DEFAULT 0,
            ca01 INTEGER DEFAULT 0, ca02 INTEGER DEFAULT 0, ca03 INTEGER DEFAULT 0,
            ce01 INTEGER DEFAULT 0, ce02 INTEGER DEFAULT 0, ce03 INTEGER DEFAULT 0,
            cns01 INTEGER DEFAULT 0, cns02 INTEGER DEFAULT 0, cns03 INTEGER DEFAULT 0,
            cns04 INTEGER DEFAULT 0, cns05 INTEGER DEFAULT 0, cns06 INTEGER DEFAULT 0,
            cns07 INTEGER DEFAULT 0, cns08 INTEGER DEFAULT 0, cns09 INTEGER DEFAULT 0,
            cns10 INTEGER DEFAULT 0, cns11 INTEGER DEFAULT 0, cns12 INTEGER DEFAULT 0,
            cns13 INTEGER DEFAULT 0, cns14 INTEGER DEFAULT 0, cns15 INTEGER DEFAULT 0,
            cns16 INTEGER DEFAULT 0, cns17 INTEGER DEFAULT 0, cns18 INTEGER DEFAULT 0,
            cns19 INTEGER DEFAULT 0, cns20 INTEGER DEFAULT 0,
            cr01 INTEGER DEFAULT 0, cr02 INTEGER DEFAULT 0, cr03 INTEGER DEFAULT 0,
            cr04 INTEGER DEFAULT 0, cr05 INTEGER DEFAULT 0, cr07 INTEGER DEFAULT 0,
            ct01 INTEGER DEFAULT 0, ct02 INTEGER DEFAULT 0,
            cd01 INTEGER DEFAULT 0, cd02 INTEGER DEFAULT 0, cd03 INTEGER DEFAULT 0,
            cd04 INTEGER DEFAULT 0,
            cs01 INTEGER DEFAULT 0, cs02 INTEGER DEFAULT 0,
            cfa01 INTEGER DEFAULT 0, cfa02 INTEGER DEFAULT 0, cfa03 INTEGER DEFAULT 0,
            cfa04 INTEGER DEFAULT 0, cfa05 INTEGER DEFAULT 0,
            cfs01 INTEGER DEFAULT 0, cfs02 INTEGER DEFAULT 0, cfs03 INTEGER DEFAULT 0,
            cfs04 INTEGER DEFAULT 0, cfs05 INTEGER DEFAULT 0,
            UNIQUE(cbsa_code, bg_geoid)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✓ Database tables created")


def init_cbsas():
    """Initialize CBSA records"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    for code, name in CBSA_MAPPING.items():
        cursor.execute(
            "INSERT OR IGNORE INTO cbsas (cbsa_code, cbsa_name) VALUES (?, ?)",
            (code, name)
        )
    
    conn.commit()
    conn.close()
    print("✓ CBSAs initialized")


def load_blockgroup_geometries(data_dir):
    """Load block group geometries from CSV files"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    for cbsa_code in CBSA_MAPPING.keys():
        bg_file = Path(data_dir) / f"{cbsa_code}_blockgroups2023.csv"
        
        if not bg_file.exists():
            print(f"  - Skipping {bg_file.name} (not found)")
            continue
        
        print(f"  Loading geometries from {bg_file.name}")
        df = pd.read_csv(bg_file)
        
        for _, row in df.iterrows():
            bg_geoid = str(row["bgrp"]).strip()
            geometry = str(row["geometry"]).strip()
            
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO blockgroups (cbsa_code, bg_geoid, geometry) VALUES (?, ?, ?)",
                    (cbsa_code, bg_geoid, geometry)
                )
            except Exception as e:
                continue
        
        conn.commit()
        print(f"    ✓ Loaded {len(df)} geometries for CBSA {cbsa_code}")
    
    conn.close()


def load_wac_data(data_dir):
    """Load WAC employment data from CSV files"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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
        # Use the _all2023.csv file which contains WAC data
        wac_file = Path(data_dir) / f"{cbsa_code}_all2023.csv"
        
        if not wac_file.exists():
            print(f"  - Skipping {wac_file.name} (not found)")
            continue
        
        print(f"  Loading WAC data from {wac_file.name}")
        df = pd.read_csv(wac_file)
        
        # The bgrp column contains the block group GEOID
        if "bgrp" not in df.columns:
            print(f"    Error: bgrp column not found in {wac_file.name}")
            continue
        
        total_jobs_cbsa = 0
        
        for _, row in df.iterrows():
            try:
                bg_geoid = str(row["bgrp"]).strip()
                
                # Build insert values - convert column names to lowercase
                values = {}
                for col in wac_columns:
                    col_upper = col.upper()
                    if col_upper in df.columns:
                        val = row[col_upper]
                        values[col] = int(val) if pd.notna(val) else 0
                    else:
                        values[col] = 0
                
                total_jobs_cbsa += values.get("c000", 0)
                
                # Prepare insert statement
                cols = ", ".join(["cbsa_code", "bg_geoid"] + list(values.keys()))
                placeholders = ", ".join(["?"] * (len(values) + 2))
                insert_values = [cbsa_code, bg_geoid] + list(values.values())
                
                cursor.execute(
                    f"INSERT OR IGNORE INTO wac_data ({cols}) VALUES ({placeholders})",
                    insert_values
                )
                
            except Exception as e:
                print(f"    Error processing row: {e}")
                continue
        
        conn.commit()
        
        # Update CBSA total jobs
        cursor.execute(
            "UPDATE cbsas SET total_jobs = ? WHERE cbsa_code = ?",
            (total_jobs_cbsa, cbsa_code)
        )
        conn.commit()
        
        print(f"    ✓ Loaded {len(df)} WAC records for CBSA {cbsa_code}")
    
    conn.close()


if __name__ == "__main__":
    # Determine data directory
    data_dir = Path(".") if len(sys.argv) == 1 else Path(sys.argv[1])
    print(f"Loading data from: {data_dir}")
    
    try:
        print("Creating database...")
        init_database()
        
        print("Initializing CBSAs...")
        init_cbsas()
        
        print("Loading block group geometries...")
        load_blockgroup_geometries(data_dir)
        
        print("Loading WAC employment data...")
        load_wac_data(data_dir)
        
        print("✓ Data loading complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
