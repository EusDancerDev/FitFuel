"""
API Package for FitFuel Backend
Contains route definitions and API schemas
"""

from fastapi import FastAPI
from .routes import auth, menu, statistics, watch_data

def init_app() -> FastAPI:
    app = FastAPI(title="FitFuel API")
    
    # Register routes
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(menu.router, prefix="/menu", tags=["Menu"])
    app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
    app.include_router(watch_data.router, prefix="/watch-data", tags=["Watch Data"])
    
    return app 