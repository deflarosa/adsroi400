
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configurazioni chiave
    HAIRCUT: float = 0.30        # taglio advertiser (30% del fatturato)
    TARGET_ROI_NETTO: float = 1.0
    PAYOUT_LORDO: float = 19.0   # €/vendita
    USE_PAYOUT_MODE: bool = True # True = usa payout netto per ricavi; False = usa fatturato

settings = Settings()


# --- Auth Config ---
ADMIN_USERNAME: str = "admin"
ADMIN_PASSWORD: str = "roi400"
SECRET_KEY: str = "change-this-secret-key"
SESSION_EXPIRE_HOURS: int = 12
