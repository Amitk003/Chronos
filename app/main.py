from fastapi import FastAPI

app = FastAPI(title="Chronos")


@app.get("/health")
async def health():
    return {"status": "operational"}
