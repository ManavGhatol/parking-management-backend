from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, slots, vehicles

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automated Parking Management System API",
    description="API for managing parking slots, vehicle entry/exit, payments, and users.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:5173", # Vite default React dev port
    "http://127.0.0.1:5173",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "https://parking-management-frontend-juqo.onrender.com",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(slots.router)
app.include_router(vehicles.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Automated Parking Management System API"}
