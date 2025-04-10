import os
from contextlib import asynccontextmanager
import uvicorn
from sqlmodel import Session
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import engine
from app.api.main import api_router
from app.models import Settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 启动中...")
    yield
    print("🛑 关闭中...")

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.environ['WDM_LOCAL'] = '1'




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
