from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.session import create_all_tables


app = FastAPI(lifespan=create_all_tables)
