from fastapi import FastAPI
from app.routes import router
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="Exam AI")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Exam AI running"}
