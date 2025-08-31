#!/usr/bin/env python3
"""
Абсолютно минимальное рабочее приложение FastAPI
"""
from fastapi import FastAPI
import uvicorn

# Создаем минимальное приложение
app = FastAPI(title="SIRIUS MINIMAL")

@app.get("/")
async def root():
    return {"message": "SIRIUS MINIMAL SERVER WORKS!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Запускаем минимальный сервер...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
