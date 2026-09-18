from pydantic import BaseModel


class EnvironmentalInput(BaseModel):
    soil_organic_carbon: float | None = None
    soil_ph: float | None = None
    soil_moisture: float | None = None
    rainfall: str | None = None
    temperature: float | None = None
    land_use: str | None = None
    crop: str | None = None
    biodiversity_index: float | None = None
    region: str | None = None