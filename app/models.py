
from sqlalchemy import Column, Integer, Float, String, Date, Time, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class CampaignData(Base):
    __tablename__ = "campagne_dati"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, index=True)
    ora = Column(String, index=True)  # 'HH:MM'
    piattaforma = Column(String, index=True)  # 'Google Ads' | 'Facebook Ads'
    prodotto = Column(String, index=True)
    campagna = Column(String, index=True)
    adset = Column(String, nullable=True)

    impression = Column(Integer, default=0)
    clic = Column(Integer, default=0)
    conversioni = Column(Integer, default=0)
    vendite = Column(Integer, default=0)

    spesa = Column(Float, default=0.0)
    fatturato_lordo = Column(Float, default=0.0)

    # calcolati e salvati per velocità (opzionale)
    fatturato_netto = Column(Float, default=0.0)
    ricavi_net = Column(Float, default=0.0)
    roi_net = Column(Float, default=0.0)
    roas_lordo = Column(Float, default=0.0)
    roas_net = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)

class DailyReport(Base):
    __tablename__ = "report_giornaliero"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, index=True)
    piattaforma = Column(String, index=True)
    prodotto = Column(String, index=True)

    spesa = Column(Float, default=0.0)
    fatturato_lordo = Column(Float, default=0.0)
    fatturato_netto = Column(Float, default=0.0)
    ricavi_net = Column(Float, default=0.0)
    roi_net = Column(Float, default=0.0)
    roas_lordo = Column(Float, default=0.0)
    roas_net = Column(Float, default=0.0)
    vendite = Column(Integer, default=0)
    lead = Column(Integer, default=0)
    cpa = Column(Float, default=0.0)

    note = Column(String, default="")
    decisione_ai = Column(String, default="")
