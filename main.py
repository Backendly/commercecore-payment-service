from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.session import create_all_tables
from pydantic import ValidationError
from routes.payment_method_routes import router as payment_method_router


app = FastAPI(lifespan=create_all_tables)
app.include_router(payment_method_router)


@app.exception_handler(ValidationError)
async def handle_validation_exception(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"description": exc.errors()},
    )
