from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.session import create_all_tables
from pydantic import ValidationError
from routes.payment_method_routes import router as payment_method_router
from routes.transaction_routes import router as transaction_router
from routes.account_routes import router as account_router

app = FastAPI(
    lifespan=create_all_tables,
    docs_url="/api/v1/docs",
    redoc_url=None,
    title="CommerceCore Payment Microservce",
    version="1.0.0",
)
app.include_router(payment_method_router)
app.include_router(transaction_router)
app.include_router(account_router)


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
