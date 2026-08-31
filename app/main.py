# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.database.base import Base
# from app.database.connection import engine
# from app.database import models
# from app.api.auth import router as auth_router

# # Create database tables
# Base.metadata.create_all(bind=engine)

# # Create FastAPI application
# app = FastAPI(
#     title="Secure Chat Application",
#     description="End-to-End Encrypted Chat Application with AI Features",
#     version="1.0.0"
# )

# # Enable React frontend communication
# app.add_middleware(

#     CORSMiddleware,

#     allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # Register API routes
# app.include_router(auth_router)

# # Home route
# @app.get("/")
# def home():
#     return {
#         "message": "Secure Chat Backend Running",
#         "status": "success"
#     }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.messages import router as messages_router
from app.api.user import router as users_router
from app.api.websocket import router as websocket_router
from app.database.base import Base
from app.database.connection import engine

# Import models before create_all().
from app.database.models import Message, User

from app.api.ai import router as ai_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Chat API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(messages_router)
app.include_router(websocket_router)
app.include_router(ai_router)

@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Secure Chat Backend Running",
    }
