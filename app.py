
import time
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.auth import auth_routes
from src.entregas import entregas_routes
from src.db import models
from src.db.database import engine
from src.configs.logger_config import logger

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url} - Status: {response.status_code} - Duration: {duration:.2f}s")
    return response

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled exception for {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error_log": error_trace
        },
    )

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(entregas_routes.router, prefix="/entregas", tags=["entregas"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the SunterCode Tracking API"}
