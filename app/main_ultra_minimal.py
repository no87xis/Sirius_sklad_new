from fastapi import FastAPI

# Create FastAPI app БЕЗ ВСЕГО
app = FastAPI(title="SIRIUS ULTRA MINIMAL")

@app.get("/")
async def root():
    return {"message": "SIRIUS ULTRA MINIMAL WORKS!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
