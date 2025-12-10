# app.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import os
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime

app = FastAPI(title="Простое погодное приложение")

# Читаем переменные окружения
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Moscow,RU")

if not API_KEY:
    raise RuntimeError("Не задан OPENWEATHER_API_KEY в .env")

URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru"

# Включаем встроенные метрики Prometheus
Instrumentator().instrument(app).expose(app)

@app.get("/", response_class=HTMLResponse)
async def get_weather():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(URL)
            r.raise_for_status()
            data = r.json()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"].capitalize()
            city_name = data["name"]

            html = f"""
            <html>
                <head>
                    <title>Погода прямо сейчас</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 80px; background: #f0f8ff; }}
                        .card {{ display: inline-block; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                        h1 {{ font-size: 72px; margin: 10px; }}
                        h2 {{ color: #555; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h2>Текущая погода</h2>
                        <h3>{city_name}</h3>
                        <h1>{temp} °C</h1>
                        <p>Ощущается как {feels_like} °C</p>
                        <p>{description}</p>
                        <small>Обновлено: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</small>
                    </div>
                </body>
            </html>
            """
            return HTMLResponse(html)
        except Exception as e:
            raise HTTPException(status_code=502, detail="Ошибка получения погоды")

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}