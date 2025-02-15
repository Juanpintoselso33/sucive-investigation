"""
Orquestador principal actualizado
"""
import hydra
from omegaconf import DictConfig
from src.processors import economic, prices, taxes, fuels, geo, exchange_rates
import os

@hydra.main(config_path="../config", config_name="main", version_base="1.2")
def process_data(cfg: DictConfig):
    """Main processing function with improved configuration handling"""
    # Validate environment
    if "PROJECT_ROOT" not in os.environ:
        raise ValueError("PROJECT_ROOT environment variable must be set")
    
    print(f"Processing data with configuration from {cfg.paths.root}")
    
    # Procesamiento económico
    valor_2020, deflator_df = economic.process_gdp_deflator(
        cfg.data.raw.gdp_deflator.file
    )
    
    gdp_df = economic.process_gdp(
        cfg.data.raw.gdp.file,
        cfg.data.raw.gdp_deflator.file,
        cfg.data.processed.gdp.file,
        cfg.years
    )
    
    # Procesamiento de precios
    cpi_df = prices.process_cpi(
        cfg.data.raw.cpi.file,
        cfg.data.processed.cpi.file,
        cfg.years
    )
    
    # Procesamiento de tipo de cambio
    tc_2020, tc_df = exchange_rates.process_exchange_rate(
        cfg.data.raw.exchange_rate.file,
        cfg.data.processed.exchange_rate.file,
        cfg.years
    )
    
    # Procesamiento de patentes
    taxes.process_vehicle_tax(
        cfg.data.raw.subnational_income.file,
        cfg.data.processed.cpi.file,
        cfg.data.processed.vehicle_tax.file,
        cfg.years,
        tc_2020  # Usamos el tipo de cambio 2020 calculado
    )
    
    # Procesamiento de combustibles
    fuels.process_gasoline(
        cfg.data.raw.gasoline.file,
        cfg.data.processed.gasoline.file,
        cfg.years,
        cpi_df,
        tc_2020
    )
    
    fuels.process_diesel(
        cfg.data.raw.diesel.file,
        cfg.data.processed.diesel.file,
        cfg.years,
        cpi_df,
        tc_2020
    )
    
    # Procesamiento de participación PIB departamental
    economic.process_gdp_share_raw(
        cfg.data.raw.subnational_gdp_share.dir,
        cfg.data.processed.subnational_gdp_share.file,
        cfg.years
    )
    
    # Procesamiento geográfico
    geo.process_shapefile(
        input_dir=os.path.join(cfg.data.raw.base_dir, os.path.dirname(cfg.data.raw.shapefile.file)),
        output_dir=os.path.join(cfg.data.processed.base_dir, "shapefiles")
    )

    # Devolver la configuración completa para usar en la notebook
    return cfg

if __name__ == "__main__":
    process_data()
