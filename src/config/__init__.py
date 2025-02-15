from dataclasses import dataclass
from typing import Optional
from omegaconf import MISSING

@dataclass
class FileConfig:
    file: str
    format: Optional[str] = None
    frequency: Optional[str] = None

@dataclass
class DataConfig:
    @dataclass
    class RawConfig:
        base_dir: str = MISSING
        gdp_deflator: FileConfig = MISSING
        cpi: FileConfig = MISSING
        gdp: FileConfig = MISSING
        subnational_income: FileConfig = MISSING
        shapefile: FileConfig = MISSING
        gasoline: dict = MISSING
        diesel: dict = MISSING
    
    @dataclass
    class ProcessedConfig:
        base_dir: str = MISSING
        gdp: FileConfig = MISSING
        cpi: FileConfig = MISSING
        vehicle_tax: FileConfig = MISSING
        shapefile: FileConfig = MISSING
        gasoline: FileConfig = MISSING
        diesel: FileConfig = MISSING


    raw: RawConfig = MISSING
    processed: ProcessedConfig = MISSING

__all__ = ['DataConfig'] 