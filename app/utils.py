
from .settings import settings

INF = 10**12

def compute_metrics(spesa: float, fatturato_lordo: float, vendite: int, clic: int):
    # Ricavi netti in due modalità
    if settings.USE_PAYOUT_MODE:
        payout_netto = settings.PAYOUT_LORDO * (1 - settings.HAIRCUT)
        ricavi_net = max(0.0, vendite * payout_netto)
    else:
        ricavi_net = max(0.0, fatturato_lordo * (1 - settings.HAIRCUT))

    roas_lordo = (fatturato_lordo / spesa) if spesa > 0 else 0.0
    roas_net = (ricavi_net / spesa) if spesa > 0 else 0.0
    roi_net = ((ricavi_net - spesa) / spesa) if spesa > 0 else 0.0
    cpa = (spesa / vendite) if vendite > 0 else INF
    cpc = (spesa / clic) if clic > 0 else INF

    # fatturato netto utile per report
    fatturato_netto = max(0.0, fatturato_lordo * (1 - settings.HAIRCUT))

    return {
        "ricavi_net": ricavi_net,
        "roas_lordo": roas_lordo,
        "roas_net": roas_net,
        "roi_net": roi_net,
        "cpa": cpa if cpa < INF else 0.0,
        "cpc": cpc if cpc < INF else 0.0,
        "fatturato_netto": fatturato_netto
    }

def decision_engine(roi_net: float, cpa: float, trend_conv: float, roas_lordo: float, volume_conv: int, spend_oggi: float):
    # Guard-rails minimi
    payout_netto = settings.PAYOUT_LORDO * (1 - settings.HAIRCUT)
    cpa_ok = payout_netto / 2  # 6.65 con default
    if volume_conv < 3 and spend_oggi < 30:
        return "Raccogli più dati (volume basso): mantieni setup e monitora."

    # 1) Campagne “buone” (target centrato)
    if roi_net >= settings.TARGET_ROI_NETTO or roas_lordo >= (2 / (1 - settings.HAIRCUT)) or cpa <= cpa_ok:
        return "Aumenta budget +10% e bid +5% sui segmenti migliori."

    # 2) In miglioramento ma ancora sotto target
    if 0.5 <= roi_net < settings.TARGET_ROI_NETTO or (cpa_ok < cpa <= payout_netto) or trend_conv > 0:
        return "Mantieni budget; ottimizza: negative keywords/placements, nuova creatività, restringi audience."

    # 3) Scarso rendimento
    if cpa > payout_netto or roas_lordo < 2.0 or roi_net < 0:
        return "Riduci bid -15% o metti in pausa i segmenti peggiori; rialloca budget a orari/prodotti top."

    return "Micro-test: duplica best ad con nuova angle; sposta 15% budget dai peggiori ai migliori."
