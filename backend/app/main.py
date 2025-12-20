from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import news, macro, stock
import uvicorn
import os

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(macro.router, prefix="/api", tags=["macro"])
app.include_router(stock.router, prefix="/api", tags=["stock"])

@app.get("/")
def read_root():
    return {"message": "Finance Dashboard API is running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
