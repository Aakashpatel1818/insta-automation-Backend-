"""Instagram API integration routes."""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Extract user ID from token."""
    try:
        from jose import jwt
        import os
        token = credentials.credentials
        SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/accounts", response_model=dict)
async def get_connected_accounts(user_id: str = Depends(get_current_user)):
    """
    Get all connected Instagram accounts.
    """
    try:
        # TODO: Fetch from MongoDB
        # accounts = await db.instagram_accounts.find({"user_id": user_id}).to_list(length=None)
        
        return {
            "data": [
                {
                    "_id": "account_1",
                    "instagram_username": "mybrand",
                    "account_type": "business",
                    "followers_count": 1250,
                    "following_count": 450,
                    "media_count": 89,
                    "is_connected": True,
                    "last_sync": "2026-01-04T13:00:00"
                }
            ],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch Instagram accounts"
        )


@router.post("/connect", response_model=dict)
async def connect_instagram_account(
    account_data: dict,
    user_id: str = Depends(get_current_user)
):
    """
    Connect a new Instagram account.
    
    Request body:
    ```json
    {
        "access_token": "your_instagram_access_token",
        "instagram_id": "instagram_business_account_id"
    }
    ```
    """
    try:
        required_fields = ["access_token", "instagram_id"]
        missing = [f for f in required_fields if f not in account_data]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required fields: {', '.join(missing)}"
            )
        
        # TODO: Validate token with Instagram API
        # TODO: Save to MongoDB
        
        return {
            "message": "Instagram account connected successfully",
            "account_id": "new_account_id",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting Instagram account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect Instagram account"
        )


@router.delete("/accounts/{account_id}", response_model=dict)
async def disconnect_instagram_account(
    account_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Disconnect an Instagram account.
    """
    try:
        # TODO: Delete from MongoDB
        # result = await db.instagram_accounts.delete_one({
        #     "_id": ObjectId(account_id),
        #     "user_id": user_id
        # })
        # if result.deleted_count == 0:
        #     raise HTTPException(status_code=404, detail="Account not found")
        
        return {
            "message": "Instagram account disconnected successfully",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Instagram account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect Instagram account"
        )


@router.post("/sync/{account_id}", response_model=dict)
async def sync_instagram_data(
    account_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Sync latest data from Instagram for an account.
    """
    try:
        # TODO: Call Instagram Graph API
        # TODO: Update account data in MongoDB
        
        return {
            "message": "Instagram data synced successfully",
            "followers": 1250,
            "following": 450,
            "media_count": 89,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error syncing Instagram data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync Instagram data"
        )
