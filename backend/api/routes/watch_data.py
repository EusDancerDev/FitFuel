from fastapi import APIRouter, Depends
from typing import Dict, List
from ...services.watch_data import WatchDataCollector

router = APIRouter()

@router.post("/sync")
async def sync_watch_data(data: Dict):
    """Sync watch data from wearable device"""
    pass

@router.get("/summary")
async def get_activity_summary():
    """Get user's activity summary"""
    pass

@router.get("/trends")
async def get_activity_trends():
    """Get user's activity trends"""
    pass 