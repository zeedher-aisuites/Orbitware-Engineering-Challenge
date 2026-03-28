import os
import time
import json
import logging
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Any, Dict

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar variables
load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
TARGET_URL = os.getenv("TARGET_URL")

if not API_KEY or not TARGET_URL:
    logging.error("Faltan variables de entorno LLM_API_KEY o TARGET_URL")
    exit(1)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_simulated_event():
    """Llama al LLM para generar un evento JSON simulado."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Prompt estricto del desafío para generar un evento JSON con formato específico
    prompt = """
    Genera un evento JSON simulado para un agente de IA.
    El JSON DEBE tener ESTRICTAMENTE este formato, sin markdown extra:
    {
      "timestamp": "2025-06-10T12:34:56.7892",
      "sessionId": "abc123_aleatorio",
      "intent": "BookFlight_o_similar",
      "latencyMs": 120,
      "success": true,
      "confidence": 0.87
    }
    """
    
    payload: Dict[str, Any] = {
        "model": "llama-3.3-70b-versatile", # Modelo sugerido por Groq para JSON
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"} # Obligamos a que responda solo JSON
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraer el contenido de la respuesta
        content_str = data["choices"][0]["message"]["content"]
        event_json = json.loads(content_str)
        
        # Aseguramos que el timestamp sea actual (UTC) por si el LLM inventa uno viejo
        event_json["timestamp"] = datetime.now(timezone.utc).isoformat()
        return event_json
    except Exception as e:
        logging.error(f"Error generando evento con LLM: {e}")
        return None

def send_event_to_ingest(event_data: Dict[str, Any]):
    """Envía el JSON generado al endpoint /ingest del Servicio A."""
    if not TARGET_URL:
        logging.error("TARGET_URL no está configurada")
        return
    try:
        res = requests.post(TARGET_URL, json=event_data, timeout=5)
        if res.status_code == 200:
            logging.info(f"Evento ingerido OK: {event_data['intent']} (Latencia: {event_data['latencyMs']}ms)")
        else:
            logging.warning(f"Error al ingerir. Code: {res.status_code}, Detalle: {res.text}")
    except Exception as e:
        logging.error(f"Fallo de conexión con Servicio A en {TARGET_URL}: {e}")

def main():
    logging.info(f"Iniciando Servicio B (Simulador). Target: {TARGET_URL}")
    while True:
        event = generate_simulated_event()
        if event:
            send_event_to_ingest(event)
        
        # Esperar 60 segundos antes del siguiente
        logging.info("Esperando 60 segundos...")
        time.sleep(60)

if __name__ == "__main__":
    main()