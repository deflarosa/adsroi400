
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from .database import Base, engine, SessionLocal
from . import models, schemas, crud
from .utils import decision_engine
from .settings import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdOptimizer ROI 400+", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve static frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0"}

@app.post("/ingest", response_model=schemas.CampaignDataOut)
def ingest(payload: schemas.CampaignDataIn, db: Session = Depends(get_db)):
    row = crud.create_campaign_data(db, payload)
    return row

@app.post("/report/build/{day}")
def build_report(day: str, db: Session = Depends(get_db)):
    d = date.fromisoformat(day)
    crud.compute_and_store_daily_reports(db, d)
    return {"ok": True, "day": d.isoformat()}

@app.get("/report/daily/{day}", response_model=List[schemas.DailyReportOut])
def daily(day: str, db: Session = Depends(get_db)):
    d = date.fromisoformat(day)
    crud.compute_and_store_daily_reports(db, d)  # ensure up-to-date
    q = db.query(models.DailyReport).filter(models.DailyReport.data == d).all()
    return q

@app.get("/report/range", response_model=List[schemas.DailyReportOut])
def range_reports(start: str, end: str, db: Session = Depends(get_db)):
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    rows = crud.list_reports_between(db, s, e)
    return rows

@app.post("/decision")
def decision(input: schemas.DecisionIn):
    msg = decision_engine(
        roi_net=input.roi_net,
        cpa=input.cpa,
        trend_conv=input.trend_conv,
        roas_lordo=input.roas_lordo,
        volume_conv=input.volume_conv,
        spend_oggi=input.spend_oggi
    )
    return {"raccomandazione": msg}

@app.get("/config")
def config():
    return {
        "TARGET_ROI_NETTO": settings.TARGET_ROI_NETTO,
        "HAIRCUT": settings.HAIRCUT,
        "PAYOUT_LORDO": settings.PAYOUT_LORDO,
        "USE_PAYOUT_MODE": settings.USE_PAYOUT_MODE
    }

from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .auth import router as auth_router, is_authenticated

# Auth middleware: protect /static (except login.html) and API routes
EXCLUDE_PATHS = {"/health", "/login", "/logout", "/static/login.html"}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if path in EXCLUDE_PATHS or path.startswith("/static/") and path.endswith("login.html"):
            return await call_next(request)
        # protect static and API
        if path.startswith("/static/") or path.startswith("/report") or path.startswith("/ingest") or path.startswith("/decision") or path.startswith("/config"):
            if not is_authenticated(request):
                # redirect to login for static, 401 for API JSON
                if path.startswith("/static/"):
                    return RedirectResponse(url="/static/login.html", status_code=303)
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail":"Not authenticated"}, status_code=401)
        return await call_next(request)

app.add_middleware(AuthMiddleware)
app.include_router(auth_router)
