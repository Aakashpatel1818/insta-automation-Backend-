"""Rules management routes."""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from datetime import datetime
from app.db.models import Rule, RuleType, MessageResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from token."""
    try:
        from jose import jwt
        import os
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
async def list_rules(
    user_id: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None
):
    """
    Get all rules for current user with pagination.
    
    - **skip**: Number of items to skip
    - **limit**: Number of items to return
    - **is_active**: Filter by active status (optional)
    """
    try:
        # TODO: Replace with actual MongoDB query
        # query = {"user_id": user_id}
        # if is_active is not None:
        #     query["is_active"] = is_active
        # 
        # total = await db.rules.count_documents(query)
        # rules = await db.rules.find(query).skip(skip).limit(limit).to_list(length=limit)
        
        # Mock data for now
        mock_rules = [
            {
                "_id": "rule_1",
                "user_id": user_id,
                "name": "Welcome DM",
                "rule_type": "dm",
                "trigger_keywords": ["hello", "hi"],
                "action_message": "Thanks for reaching out!",
                "is_active": True,
                "success_count": 45,
                "failure_count": 2,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "data": mock_rules,
            "total": len(mock_rules),
            "skip": skip,
            "limit": limit,
            "pages": (len(mock_rules) + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Error listing rules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch rules"
        )


@router.post("/", response_model=dict)
async def create_rule(
    rule: dict,
    user_id: str = Depends(get_current_user)
):
    """
    Create a new automation rule.
    
    Request body:
    ```json
    {
        "name": "Welcome DM",
        "description": "Send welcome message",
        "rule_type": "dm",
        "trigger_keywords": ["hello", "hi"],
        "action_message": "Thanks for reaching out!",
        "is_case_sensitive": false
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["name", "rule_type", "action_message"]
        missing = [f for f in required_fields if f not in rule]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required fields: {', '.join(missing)}"
            )
        
        # Validate rule_type
        valid_types = ["comment", "dm", "follow", "unfollow"]
        if rule.get("rule_type") not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid rule_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # TODO: Insert into MongoDB
        # rule["user_id"] = user_id
        # rule["is_active"] = rule.get("is_active", True)
        # rule["created_at"] = datetime.utcnow()
        # rule["updated_at"] = datetime.utcnow()
        # result = await db.rules.insert_one(rule)
        # rule["_id"] = str(result.inserted_id)
        
        rule["_id"] = "new_rule_id"
        rule["user_id"] = user_id
        rule["created_at"] = datetime.utcnow().isoformat()
        
        return {
            "data": rule,
            "message": "Rule created successfully",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create rule"
        )


@router.get("/{rule_id}", response_model=dict)
async def get_rule(
    rule_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get a specific rule by ID.
    """
    try:
        # TODO: Fetch from MongoDB
        # rule = await db.rules.find_one({"_id": ObjectId(rule_id), "user_id": user_id})
        # if not rule:
        #     raise HTTPException(status_code=404, detail="Rule not found")
        
        rule = {
            "_id": rule_id,
            "user_id": user_id,
            "name": "Welcome DM",
            "rule_type": "dm",
            "trigger_keywords": ["hello", "hi"],
            "action_message": "Thanks for reaching out!"
        }
        
        return {"data": rule, "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch rule"
        )


@router.put("/{rule_id}", response_model=dict)
async def update_rule(
    rule_id: str,
    updates: dict,
    user_id: str = Depends(get_current_user)
):
    """
    Update an existing rule.
    """
    try:
        # TODO: Update in MongoDB
        # result = await db.rules.update_one(
        #     {"_id": ObjectId(rule_id), "user_id": user_id},
        #     {"$set": {**updates, "updated_at": datetime.utcnow()}}
        # )
        # if result.matched_count == 0:
        #     raise HTTPException(status_code=404, detail="Rule not found")
        
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        return {
            "data": updates,
            "message": "Rule updated successfully",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rule"
        )


@router.delete("/{rule_id}", response_model=dict)
async def delete_rule(
    rule_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a rule.
    """
    try:
        # TODO: Delete from MongoDB
        # result = await db.rules.delete_one({"_id": ObjectId(rule_id), "user_id": user_id})
        # if result.deleted_count == 0:
        #     raise HTTPException(status_code=404, detail="Rule not found")
        
        return {
            "message": "Rule deleted successfully",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete rule"
        )


@router.post("/{rule_id}/toggle", response_model=dict)
async def toggle_rule(
    rule_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Toggle rule active/inactive status.
    """
    try:
        # TODO: Update in MongoDB
        # rule = await db.rules.find_one({"_id": ObjectId(rule_id), "user_id": user_id})
        # new_status = not rule.get("is_active", True)
        # await db.rules.update_one({"_id": ObjectId(rule_id)}, {"$set": {"is_active": new_status}})
        
        return {
            "message": "Rule toggled successfully",
            "is_active": True,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle rule"
        )