from pydantic import BaseModel
from typing import Optional, List


class CBSABase(BaseModel):
    cbsa_code: str
    cbsa_name: str


class CBSACreate(CBSABase):
    pass


class CBSA(CBSABase):
    id: int
    total_jobs: int

    class Config:
        from_attributes = True


class BlockGroupBase(BaseModel):
    cbsa_code: str
    bg_geoid: str
    geometry: str


class BlockGroupCreate(BlockGroupBase):
    pass


class BlockGroup(BlockGroupBase):
    id: int

    class Config:
        from_attributes = True


class WACDataBase(BaseModel):
    cbsa_code: str
    bg_geoid: str
    c000: int


class WACDataResponse(WACDataBase):
    id: int
    ca01: int
    ca02: int
    ca03: int
    ce01: int
    ce02: int
    ce03: int
    cns01: int
    cns09: int
    cns16: int

    class Config:
        from_attributes = True


class FilterOptions(BaseModel):
    employment_codes: List[dict]
    age_groups: List[dict]
    earnings_brackets: List[dict]
    education_levels: List[dict]
