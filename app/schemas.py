
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class CampaignDataIn(BaseModel):
    data: date
    ora: str
    piattaforma: str
    prodotto: str
    campagna: str
    adset: Optional[str] = None
    impression: int = 0
    clic: int = 0
    conversioni: int = 0
    vendite: int = 0
    spesa: float = 0.0
    fatturato_lordo: float = 0.0

class CampaignDataOut(CampaignDataIn):
    id: int
    fatturato_netto: float
    ricavi_net: float
    roi_net: float
    roas_lordo: float
    roas_net: float
    cpa: float
    cpc: float

    class Config:
        from_attributes = True

class DailyReportOut(BaseModel):
    id: int
    data: date
    piattaforma: str
    prodotto: str
    spesa: float
    fatturato_lordo: float
    fatturato_netto: float
    ricavi_net: float
    roi_net: float
    roas_lordo: float
    roas_net: float
    vendite: int
    lead: int
    cpa: float
    note: str
    decisione_ai: str

    class Config:
        from_attributes = True

class DecisionIn(BaseModel):
    roi_net: float
    cpa: float
    trend_conv: float = 0.0
    roas_lordo: float = 0.0
    volume_conv: int = 0
    spend_oggi: float = 0.0

class DecisionOut(BaseModel):
    raccomandazione: str
