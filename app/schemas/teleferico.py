from pydantic import BaseModel
from typing import List

class FilterParams(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    lineas: List[str]
    hora_min: int
    hora_max: int
    dias_semana: List[str]

class PredictParams(BaseModel):
    filters: FilterParams
    linea: str
    dias_pred: int
