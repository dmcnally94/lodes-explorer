from sqlalchemy import Column, Integer, String, Float, Text, Numeric, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from .db import Base


class CBSA(Base):
    __tablename__ = "cbsas"
    
    id = Column(Integer, primary_key=True, index=True)
    cbsa_code = Column(String(5), unique=True, index=True, nullable=False)
    cbsa_name = Column(String(255), nullable=False)
    total_jobs = Column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_cbsa_code", "cbsa_code"),
    )


class BlockGroup(Base):
    __tablename__ = "blockgroups"
    
    id = Column(Integer, primary_key=True, index=True)
    cbsa_code = Column(String(5), nullable=False, index=True)
    bg_geoid = Column(String(12), nullable=False)  # Block group FIPS code
    geometry = Column(Text, nullable=False)  # GeoJSON string
    
    __table_args__ = (
        Index("ix_bg_cbsa", "cbsa_code"),
        Index("ix_bg_geoid", "bg_geoid"),
        UniqueConstraint("cbsa_code", "bg_geoid", name="uq_cbsa_bg"),
    )


class WACData(Base):
    __tablename__ = "wac_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cbsa_code = Column(String(5), nullable=False, index=True)
    bg_geoid = Column(String(12), nullable=False, index=True)
    
    # Total jobs
    c000 = Column(Integer, default=0)
    
    # Age categories (CA01, CA02, CA03)
    ca01 = Column(Integer, default=0)
    ca02 = Column(Integer, default=0)
    ca03 = Column(Integer, default=0)
    
    # Earnings (CE01, CE02, CE03)
    ce01 = Column(Integer, default=0)
    ce02 = Column(Integer, default=0)
    ce03 = Column(Integer, default=0)
    
    # NAICS sectors (CNS01-CNS20)
    cns01 = Column(Integer, default=0)
    cns02 = Column(Integer, default=0)
    cns03 = Column(Integer, default=0)
    cns04 = Column(Integer, default=0)
    cns05 = Column(Integer, default=0)
    cns06 = Column(Integer, default=0)
    cns07 = Column(Integer, default=0)
    cns08 = Column(Integer, default=0)
    cns09 = Column(Integer, default=0)
    cns10 = Column(Integer, default=0)
    cns11 = Column(Integer, default=0)
    cns12 = Column(Integer, default=0)
    cns13 = Column(Integer, default=0)
    cns14 = Column(Integer, default=0)
    cns15 = Column(Integer, default=0)
    cns16 = Column(Integer, default=0)
    cns17 = Column(Integer, default=0)
    cns18 = Column(Integer, default=0)
    cns19 = Column(Integer, default=0)
    cns20 = Column(Integer, default=0)
    
    # Race (CR01-CR05, CR07)
    cr01 = Column(Integer, default=0)
    cr02 = Column(Integer, default=0)
    cr03 = Column(Integer, default=0)
    cr04 = Column(Integer, default=0)
    cr05 = Column(Integer, default=0)
    cr07 = Column(Integer, default=0)
    
    # Ethnicity (CT01, CT02)
    ct01 = Column(Integer, default=0)
    ct02 = Column(Integer, default=0)
    
    # Education (CD01-CD04)
    cd01 = Column(Integer, default=0)
    cd02 = Column(Integer, default=0)
    cd03 = Column(Integer, default=0)
    cd04 = Column(Integer, default=0)
    
    # Sex (CS01, CS02)
    cs01 = Column(Integer, default=0)
    cs02 = Column(Integer, default=0)
    
    # Firm age (CFA01-CFA05)
    cfa01 = Column(Integer, default=0)
    cfa02 = Column(Integer, default=0)
    cfa03 = Column(Integer, default=0)
    cfa04 = Column(Integer, default=0)
    cfa05 = Column(Integer, default=0)
    
    # Firm size (CFS01-CFS05)
    cfs01 = Column(Integer, default=0)
    cfs02 = Column(Integer, default=0)
    cfs03 = Column(Integer, default=0)
    cfs04 = Column(Integer, default=0)
    cfs05 = Column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_wac_cbsa", "cbsa_code"),
        Index("ix_wac_bg", "bg_geoid"),
        Index("ix_wac_cbsa_bg", "cbsa_code", "bg_geoid"),
        UniqueConstraint("cbsa_code", "bg_geoid", name="uq_wac_cbsa_bg"),
    )
