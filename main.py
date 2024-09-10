from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.session import create_all_tables
from pydantic import ValidationError
from routes.payment_method_routes import router as payment_method_router


app = FastAPI(lifespan=create_all_tables, docs_url="/api/v1/docs", redoc_url=None)
app.include_router(payment_method_router)


@app.exception_handler(422)
async def handle_validation_exception(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "meta": {
                "success": False,
                "status_code": 422,
                "request_method": str(request.method),
                "request_path": str(request.url),
            },
            "details": {"message": exc.errors()},
        },
    )


@app.exception_handler(500)
async def handle_internal_server_exception(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "meta": {
                "success": False,
                "status_code": 500,
                "request_method": str(request.method),
                "request_path": str(request.url),
            },
            "details": {
                "message": str(exc),
            },
        },
    )


@app.exception_handler(404)
async def handle_not_found_exception(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "meta": {
                "success": False,
                "status_code": 404,
                "request_method": str(request.method),
                "request_path": str(request.url),
            },
            "details": {
                "message": str(exc),
            },
        },
    )
