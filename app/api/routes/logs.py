"""Logs and analytics routes."""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()



from jose import jwt
import os

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from token."""
    try:
        token = credentials.credentials
        SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        if not SECRET_KEY:
          raise ValueError("JWT_SECRET_KEY environment variable is required")
        ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/", response_model=dict)
async def get_logs(
    user_id: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    log_type: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Query(7, ge=1, le=365)
):
    """
    Get activity logs with filters.
    
    - **skip**: Number of items to skip
    - **limit**: Number of items to return (max 100)
    - **log_type**: Filter by type (comment, dm, follow, error)
    - **status**: Filter by status (success, failed, pending)
    - **days**: Get logs from last N days
    """
    try:
        # TODO: Query MongoDB with filters
        # query = {"user_id": user_id}
        # start_date = datetime.utcnow() - timedelta(days=days)
        # query["created_at"] = {"$gte": start_date}
        # 
        # if log_type:
        #     query["log_type"] = log_type
        # if status:
        #     query["status"] = status
        # 
        # total = await db.logs.count_documents(query)
        # logs = await db.logs.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        mock_logs = [
            {
                "_id": "log_1",
                "user_id": user_id,
                "log_type": "comment",
                "status": "success",
                "message": "Commented on @username post",
                "target_username": "username",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "data": mock_logs,
            "total": len(mock_logs),
            "skip": skip,
            "limit": limit,
            "pages": (len(mock_logs) + limit - 1) // limit,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch logs"
        )


@router.get("/stats/summary", response_model=dict)
async def get_summary_stats(user_id: str = Depends(get_current_user)):
    """
    Get summary statistics.
    """
    try:
        # TODO: Aggregate data from MongoDB
        # logs = await db.logs.find({"user_id": user_id}).to_list(length=None)
        # 
        # total_comments = len([l for l in logs if l["log_type"] == "comment"])
        # total_dms = len([l for l in logs if l["log_type"] == "dm"])
        # success_count = len([l for l in logs if l["status"] == "success"])
        # failed_count = len([l for l in logs if l["status"] == "failed"])
        
        return {
            "total_comments": 156,
            "total_dms": 89,
            "total_follows": 42,
            "total_actions": 287,
            "success_count": 273,
            "failed_count": 14,
            "success_rate": 95.1,
            "active_rules": 5,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching summary stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/stats/daily", response_model=dict)
async def get_daily_stats(
    user_id: str = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365)
):
    """
    Get daily statistics for last N days.
    """
    try:
        # TODO: Aggregate daily data from MongoDB
        daily_stats = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            daily_stats.append({
                "date": date.strftime("%Y-%m-%d"),
                "total_comments": 5 + i,
                "total_dms": 3 + i,
                "total_follows": 2 + i,
                "total_actions": 10 + (i*2),
                "success_count": 9 + i,
                "failure_count": 1
            })
        
        return {
            "data": daily_stats,
            "days": days,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching daily stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch daily statistics"
        )


@router.delete("/", response_model=dict)
async def clear_logs(
    user_id: str = Depends(get_current_user),
    days_old: int = Query(30, ge=1)
):
    """
    Clear logs older than specified days.
    """
    try:
        # TODO: Delete from MongoDB
        # cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        # result = await db.logs.delete_many({
        #     "user_id": user_id,
        #     "created_at": {"$lt": cutoff_date}
        # })
        
        return {
            "message": f"Deleted logs older than {days_old} days",
            "deleted_count": 45,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear logs"
        )
