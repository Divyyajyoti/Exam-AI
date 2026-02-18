from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Exam AI", version="0.1.0")
app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Exam AI running"}
