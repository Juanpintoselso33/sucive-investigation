"""
Orquestador principal actualizado
"""
import hydra
from omegaconf import DictConfig
from src.processors import economic, prices, taxes, fuels, geo, exchange_rates
from src.estimators import population as pop_estimator
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

    # Sección de estimaciones
    pop_estimator.project_population(
        cfg.data.raw.population_census.file,
        cfg.data.estimated.projected_population.file,
        cfg.years
    )   
    
    # Procesamiento de participación PIB departamental proyectada
    economic.project_subnational_gdp_share(
        cfg.data.processed.subnational_gdp_share.dir,
        cfg.data.estimated.projected_subnational_gdp_share.file,
        cfg.years
    )
    
    # Estimar PIB departamental
    economic.estimate_subnational_gdp(
        gdp_share_path=cfg.data.estimated.projected_subnational_gdp_share.file,
        national_gdp_path=cfg.data.processed.gdp.file,
        output_path=cfg.data.estimated.projected_subnational_gdp.file,
        years_params=cfg.years
    )
    
    # Estimar datos faltantes de patentes
    taxes.estimate_missing_vehicle_tax(
        cfg.data.processed.vehicle_tax.file,
        cfg.data.estimated.projected_population.file,
        cfg.data.estimated.estimated_montevideo_vehicle_tax.file,
        cfg.years,
        target_dept='Montevideo',
        treatment_year=2007
    )
    
    # Crear dataset final combinando estimaciones y datos reales
    taxes.create_final_vehicle_tax(
        cfg.data.processed.vehicle_tax.file,
        cfg.data.estimated.estimated_montevideo_vehicle_tax.file,
        cfg.data.final.vehicle_tax.file,
        treatment_year=2007
    )

    # Devolver la configuración completa para usar en la notebook
    return cfg

if __name__ == "__main__":
    process_data()
