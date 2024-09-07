from fastapi import FastAPI
from db.session import create_all_tables


app = FastAPI(lifespan=create_all_tables)
