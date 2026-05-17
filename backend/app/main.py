from fastapi import FastAPI
from app.routes.upload import router as upload_router
import asyncio
import sys
from fastapi.middleware.cors import CORSMiddleware



if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )

app = FastAPI(title="Screenschot analysis API", version="1.0.0")

app.include_router(upload_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cart-comparator-manomay2-hbhzd02x1-manomay-projects.vercel.app",
        "https://cart-comparator.vercel.app",
        "http://localhost:3000"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message" : "Backend Running Successfully"}
