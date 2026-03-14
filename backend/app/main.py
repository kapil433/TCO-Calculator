"""
TCO Calculator API — FastAPI app.
Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Swagger UI: http://localhost:8000/docs
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_V1_PREFIX, CORS_ORIGINS
from app.api.v1 import tco

logger = logging.getLogger("tco.scheduler")
_SCRAPE_INTERVAL_SECONDS = 7 * 24 * 3600  # 7 days


async def _fuel_price_scheduler():
    """Background task: check if fuel prices are stale and re-scrape weekly."""
    await asyncio.sleep(5)  # let the app finish starting
    while True:
        try:
            from scripts.scrape_fuel_prices import is_stale, run_scrape
            if is_stale():
                logger.info("Fuel prices are stale (>7 days). Starting scrape...")
                result = await asyncio.to_thread(run_scrape, force=False)
                if result.get("skipped"):
                    logger.info("Scrape skipped: %s", result.get("reason"))
                else:
                    logger.info(
                        "Scrape complete: %s scraped, %s fallback. Updated: %s",
                        result.get("states_scraped"),
                        result.get("states_fallback"),
                        result.get("last_updated"),
                    )
            else:
                logger.info("Fuel prices are fresh. Next check in %d hours.", _SCRAPE_INTERVAL_SECONDS // 3600)
        except Exception as e:
            logger.warning("Fuel price scheduler error (will retry): %s", e)
        await asyncio.sleep(_SCRAPE_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_fuel_price_scheduler())
    logger.info("Fuel price scheduler started (interval: %d days)", _SCRAPE_INTERVAL_SECONDS // 86400)
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="TCO Calculator API",
    description="Total Cost of Ownership for 4-Wheeler PV in India — backend for React frontend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tco.router, prefix=API_V1_PREFIX)


@app.get("/")
def root():
    return {"app": "TCO Calculator API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    from app.data.fuel_prices import get_fuel_price_status
    return {"status": "ok", "fuel_prices": get_fuel_price_status()}
