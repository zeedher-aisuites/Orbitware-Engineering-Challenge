import os
import time
import json
import logging
import threading
import requests
from fastapi import FastAPI
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

app = FastAPI(title="Orbitware - Servicio B (Simulador)")
API_KEY = os.getenv("LLM_API_KEY")
TARGET_URL = os.getenv("TARGET_URL")

@app.get("/")
@app.get("/health")
def health_check() -> Dict[str, Optional[str]]:
    return {"status": "running", "target": TARGET_URL}

def simulator_loop():
    logging.info(f"Iniciando ciclo del simulador. Target: {TARGET_URL}")
    if not TARGET_URL:
        logging.error("TARGET_URL no está configurada en las variables de entorno")
        return
    while True:
        try:
            # Lógica del simulador (idéntica a la anterior)
            headers: Dict[str, str] = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
            prompt = "Genera un evento JSON simulado para un agente de IA. Formato estricto: timestamp, sessionId, intent, latencyMs, success, confidence."
            payload: Dict[str, Any] = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                event_data = json.loads(response.json()["choices"][0]["message"]["content"])
                event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
                
                res = requests.post(TARGET_URL, json=event_data, timeout=5)
                logging.info(f"Evento enviado a {TARGET_URL}. Status: {res.status_code}")
            
        except Exception as e:
            logging.error(f"Error en simulador: {e}")
        
        time.sleep(60)

# Iniciamos el simulador en un hilo aparte
threading.Thread(target=simulator_loop, daemon=True).start()