
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import date
from . import models
from .utils import compute_metrics
from .settings import settings

def create_campaign_data(db: Session, payload):
    m = compute_metrics(payload.spesa, payload.fatturato_lordo, payload.vendite, payload.clic)
    row = models.CampaignData(
        data=payload.data,
        ora=payload.ora,
        piattaforma=payload.piattaforma,
        prodotto=payload.prodotto,
        campagna=payload.campagna,
        adset=payload.adset,
        impression=payload.impression,
        clic=payload.clic,
        conversioni=payload.conversioni,
        vendite=payload.vendite,
        spesa=payload.spesa,
        fatturato_lordo=payload.fatturato_lordo,
        fatturato_netto=m["fatturato_netto"],
        ricavi_net=m["ricavi_net"],
        roi_net=m["roi_net"],
        roas_lordo=m["roas_lordo"],
        roas_net=m["roas_net"],
        cpa=m["cpa"],
        cpc=m["cpc"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def get_daily_report(db: Session, day: date):
    # Aggrega per piattaforma+prodotto
    q = db.query(
        models.CampaignData.piattaforma,
        models.CampaignData.prodotto,
        func.sum(models.CampaignData.spesa).label("spesa"),
        func.sum(models.CampaignData.fatturato_lordo).label("fatt_lordo"),
        func.sum(models.CampaignData.fatturato_netto).label("fatt_netto"),
        func.sum(models.CampaignData.ricavi_net).label("ricavi_net"),
        func.sum(models.CampaignData.vendite).label("vendite"),
        func.avg(models.CampaignData.roas_lordo).label("roas_lordo_avg"),
        func.avg(models.CampaignData.roas_net).label("roas_net_avg"),
        func.avg(models.CampaignData.roi_net).label("roi_net_avg"),
        func.avg(models.CampaignData.cpa).label("cpa_avg")
    ).filter(models.CampaignData.data == day).group_by(
        models.CampaignData.piattaforma, models.CampaignData.prodotto
    ).all()
    return q

def compute_and_store_daily_reports(db: Session, day: date):
    rows = get_daily_report(db, day)
    # elimina report esistenti per il giorno (rebuild idempotente)
    db.query(models.DailyReport).filter(models.DailyReport.data == day).delete()
    for r in rows:
        rep = models.DailyReport(
            data=day,
            piattaforma=r.piattaforma,
            prodotto=r.prodotto,
            spesa=float(r.spesa or 0),
            fatturato_lordo=float(r.fatt_lordo or 0),
            fatturato_netto=float(r.fatt_netto or 0),
            ricavi_net=float(r.ricavi_net or 0),
            roi_net=float(r.roi_net_avg or 0),
            roas_lordo=float(r.roas_lordo_avg or 0),
            roas_net=float(r.roas_net_avg or 0),
            vendite=int(r.vendite or 0),
            lead=int(r.vendite or 0),  # opzionale: usa vendite come proxy dei lead
            cpa=float(r.cpa_avg or 0),
            note="",
            decisione_ai=""
        )
        db.add(rep)
    db.commit()

def list_reports_between(db: Session, start, end):
    return db.query(models.DailyReport).filter(models.DailyReport.data >= start, models.DailyReport.data <= end).order_by(models.DailyReport.data.desc()).all()
