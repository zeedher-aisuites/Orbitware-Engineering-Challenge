from fastapi import FastAPI, Response
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

app = FastAPI(title="Orbitware - Servicio A (Ingest & Metrics)")

# Almacenamiento en memoria
events_db: List[Dict[str, Any]] = []

# Modelo de validación estricta
class EventPayload(BaseModel):
    timestamp: datetime
    sessionId: str
    intent: str
    latencyMs: int
    success: bool
    confidence: float

def get_filtered_events() -> List[Dict[str, Any]]:
    """
    Aplica la lógica de rolling window:
    1. Eventos de los últimos 5 minutos.
    2. Hasta 30 eventos más recientes.
    Retorna la sublista que cumpla con ambas (la más restrictiva).
    """
    if not events_db:
        return []

    # Se asume hora actual en UTC para la comparación
    now = datetime.now(timezone.utc)
    five_mins_ago = now - timedelta(minutes=5)

    # 1. Filtrar por tiempo (últimos 5 minutos)
    time_filtered: List[Dict[str, Any]] = []
    for event in events_db:
        # Asegurar que el timestamp del evento tenga timezone (UTC) para comparar
        event_time = event["timestamp"]
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
            
        if event_time >= five_mins_ago:
            time_filtered.append(event)

    # 2. Filtrar por cantidad (máximo 30 recientes)
    # Como los eventos entran cronológicamente, tomamos los últimos 30 de la lista filtrada
    if len(time_filtered) > 30:
        return time_filtered[-30:]
    
    return time_filtered

@app.post("/ingest")
async def ingest_event(event: EventPayload):
    """
    Acepta un evento JSON, lo valida y lo almacena en memoria.
    """
    events_db.append(event.model_dump())
    return {"status": "success", "message": "Evento ingerido correctamente"}

@app.get("/report")
async def get_report() -> Dict[str, Any]:
    """
    Retorna métricas calculadas en formato JSON basadas en la rolling window.
    """
    valid_events = get_filtered_events()
    total_events = len(valid_events)

    if total_events == 0:
        return {
            "totalEvents": 0,
            "avgLatencyMs": 0.0,
            "errorRate": 0.0,
            "avgConfidence": 0.0
        }

    sum_latency = sum(e["latencyMs"] for e in valid_events)
    success_count = sum(1 for e in valid_events if e["success"])
    sum_confidence = sum(e["confidence"] for e in valid_events)

    avg_latency = sum_latency / total_events
    error_rate = 1.0 - (success_count / total_events)
    avg_confidence = sum_confidence / total_events

    return {
        "totalEvents": total_events,
        "avgLatencyMs": round(avg_latency, 2),
        "errorRate": round(error_rate, 3),
        "avgConfidence": round(avg_confidence, 2)
    }

@app.get("/metrics")
async def get_metrics():
    """
    Retorna métricas en formato Prometheus (texto plano).
    """
    valid_events = get_filtered_events()
    total_events = len(valid_events)

    if total_events == 0:
        avg_latency = 0.0
        error_rate = 0.0
        avg_confidence = 0.0
    else:
        success_count = sum(1 for e in valid_events if e["success"])
        avg_latency = sum(e["latencyMs"] for e in valid_events) / total_events
        error_rate = 1.0 - (success_count / total_events)
        avg_confidence = sum(e["confidence"] for e in valid_events) / total_events

    # Formato Prometheus
    prometheus_data = (
        f"voice_events_total {total_events}\n"
        f"voice_latency_ms_avg {round(avg_latency, 2)}\n"
        f"voice_error_rate {round(error_rate, 3)}\n"
        f"voice_confidence_avg {round(avg_confidence, 2)}\n"
    )
    
    return Response(content=prometheus_data, media_type="text/plain")

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {"status": "ok", "stored_events": len(events_db)}