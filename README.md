# Orbitware Engineering Challenge - Voice AI Metrics

Sistema de ingesta y monitoreo de métricas para un agente de IA, compuesto por microservicios contenerizados y desplegados en Render.

## 🚀 URLs Públicas
* **Servicio A (Metrics API):** [https://orbit-servicio-a.onrender.com/docs](https://orbit-servicio-a.onrender.com/docs)
* **Reporte en vivo (JSON):** [https://orbit-servicio-a.onrender.com/report](https://orbit-servicio-a.onrender.com/report)
* **Servicio B (LLM Simulator):** [https://orbit-servicio-b.onrender.com/health](https://orbit-servicio-b.onrender.com/health)

## 🛠️ Arquitectura y Tecnologías
* **Servicio A (FastAPI):** Ingesta distribuida con validación estricta (Pydantic). Implementa una ventana móvil (5 min / 30 eventos) para el cálculo de KPIs en tiempo real.
* **Servicio B (Python/LLM):** Simulador que utiliza **Groq (Llama-3.3)** para generar intents y datos de latencia realistas cada minuto.
* **Infraestructura:** Contenerización con **Docker** y orquestación con **Docker Compose**.

## 📦 Ejecución Local
Para replicar el entorno completo:
1. Clonar el repositorio.
2. Crear un archivo `.env` con la variable `LLM_API_KEY`.
3. Ejecutar: `docker-compose up --build`

## 📈 Endpoints Clave
* `POST /ingest`: Punto de entrada de eventos.
* `GET /report`: Análisis estadístico de la ventana móvil.
* `GET /metrics`: Formato Prometheus para monitoreo externo.