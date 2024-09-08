from fastapi import FastAPI
from db.session import create_all_tables
from routes.payment_method_routes import router as payment_method_router


app = FastAPI(lifespan=create_all_tables)
app.include_router(payment_method_router)
