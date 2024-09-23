from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from db.session import create_all_tables_and_initialize_redis_instance
from datetime import datetime
from pydantic import ValidationError
from api.v1 import (
    account_router,
    refunds_router,
    payment_method_router,
    transaction_router,
    webhooks_router,
)
import os
from jobs.payment_jobs import recieve_orders
from redis import Redis
from rq import Queue

queue = Queue(connection=Redis.from_url(os.getenv("REDIS_URL")))
queue.enqueue(recieve_orders)

app = FastAPI(
    lifespan=create_all_tables_and_initialize_redis_instance,
    docs_url="/api/v1/docs",
    redoc_url=None,
    title="CommerceCore Payment Microservce",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)
app.include_router(payment_method_router)
app.include_router(transaction_router)
app.include_router(account_router)
app.include_router(refunds_router)
app.include_router(webhooks_router)


async def error_response_structure(
    request: Request,
    exc,
    code: int,
    error: str,
):

    return {
        "error": error,
        "meta": {
            "success": False,
            "status_code": code,
            "request_method": str(request.method),
            "request_path": str(request.url),
        },
        "details": {
            "message": str(exc).split(": ")[-1],
        },
    }


@app.exception_handler(422)
async def handle_validation_exception(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content=await error_response_structure(
            request,
            exc,
            422,
            "Validation Error",
        ),
    )


@app.exception_handler(500)
async def handle_internal_server_exception(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content=await error_response_structure(
            request,
            exc,
            500,
            "Internal Server Error",
        ),
    )


@app.exception_handler(404)
async def handle_not_found_exception(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content=await error_response_structure(request, exc, 404, "Not Found"),
    )


@app.exception_handler(400)
async def handle_400_bad_request(request: Request, exc):
    return JSONResponse(
        status_code=400,
        content=await error_response_structure(request, exc, 400, "Bad Request"),
    )


@app.exception_handler(405)
async def handle_method_not_allowed(request: Request, exc):
    return JSONResponse(
        status_code=405,
        content=await error_response_structure(
            request,
            exc,
            405,
            "Method Not Allowed",
        ),
    )


@app.get("/")
async def home():
    return RedirectResponse(url="/api/v1")


@app.get("/api/v1")
async def root():
    return {
        "message": "Welcome to CommerceCore Payment Service API",
        "version": "v1",
        "timpstamp": str(datetime.now()),
        "starter_endpoints": {
            "create_connected_account": "/api/v1/connected-accounts",
            "continue_onboarding": "/api/v1/connected-accounts/onboarding",
            "login_account_dashboard": "/api/v1/connected-accounts/login",
            "create_transaction": "/api/v1/transactions",
            "confirm_transaction": "/api/v1/transactions/confirm",
            "request_refund": "/api/v1/refunds",
        },
        "documentation": "https://documenter.getpostman.com/view/36378381/2sAXqtb23",
    }


@app.get("/api/v1/status")
async def status():
    return {
        "status": "ok",
        "service": "The Payment Service",
        "timestamp": str(datetime.now()),
        "base_url": "https://commercecore-payment-service.onrender.com/api/v1",
        "database_status": "connected",
    }
