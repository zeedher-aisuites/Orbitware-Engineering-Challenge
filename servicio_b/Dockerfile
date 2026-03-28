FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Al ser un worker en segundo plano, no exponemos puertos, solo corremos el script
CMD ["python", "main.py"]