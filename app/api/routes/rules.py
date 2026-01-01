"""Rules management routes"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter()

# In-memory storage (replace with database in production)
rules_db = {}

class RuleToggle(BaseModel):
    """Toggle configuration for rule"""
    comment_only: bool = False  # true = only reply to comment
    send_dm: bool = False       # true = also send DM
    dm_message: Optional[str] = None

class Rule(BaseModel):
    """Automation rule model"""
    id: Optional[str] = None
    rule_name: str
    keywords: List[str]
    comment_reply: str
    target_account: str
    target_content_type: str  # 'post', 'reel', 'story', 'all-content'
    target_content_ids: List[str]  # specific content IDs, empty if all-content
    toggle: RuleToggle
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class RuleCreate(BaseModel):
    """Rule creation model (without id and timestamps)"""
    rule_name: str
    keywords: List[str] = Field(..., min_items=1)
    comment_reply: str
    target_account: str
    target_content_type: str
    target_content_ids: List[str] = []
    toggle: RuleToggle
    is_active: bool = True

class RuleUpdate(BaseModel):
    """Rule update model"""
    rule_name: Optional[str] = None
    keywords: Optional[List[str]] = None
    comment_reply: Optional[str] = None
    target_account: Optional[str] = None
    target_content_type: Optional[str] = None
    target_content_ids: Optional[List[str]] = None
    toggle: Optional[RuleToggle] = None
    is_active: Optional[bool] = None

class RuleToggleStatus(BaseModel):
    """Model for toggling rule active status"""
    is_active: bool

@router.get("/", response_model=dict)
async def get_rules(
    filter: Optional[str] = None,  # 'all', 'active', 'inactive'
    account: Optional[str] = None   # filter by target account
):
    """
    Get all rules with optional filtering
    
    Query Parameters:
    - filter: 'all', 'active', or 'inactive'
    - account: filter by target_account
    """
    rules = list(rules_db.values())
    
    # Apply filters
    if filter == 'active':
        rules = [r for r in rules if r.is_active]
    elif filter == 'inactive':
        rules = [r for r in rules if not r.is_active]
    
    if account:
        rules = [r for r in rules if r.target_account == account]
    
    return {
        "rules": rules,
        "count": len(rules),
        "message": "Rules retrieved successfully"
    }

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Rule)
async def create_rule(rule: RuleCreate):
    """
    Create new automation rule
    
    Validates:
    - At least one keyword must be provided
    - target_content_type must be valid
    - If not 'all-content', at least one content_id required
    """
    # Validation
    if not rule.keywords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one keyword is required"
        )
    
    valid_content_types = ['post', 'reel', 'story', 'all-content']
    if rule.target_content_type not in valid_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type. Must be one of: {valid_content_types}"
        )
    
    if rule.target_content_type != 'all-content' and not rule.target_content_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one content item must be selected for specific content types"
        )
    
    # Create rule
    rule_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    new_rule = Rule(
        id=rule_id,
        rule_name=rule.rule_name,
        keywords=rule.keywords,
        comment_reply=rule.comment_reply,
        target_account=rule.target_account,
        target_content_type=rule.target_content_type,
        target_content_ids=rule.target_content_ids,
        toggle=rule.toggle,
        is_active=rule.is_active,
        created_at=timestamp,
        updated_at=timestamp
    )
    
    rules_db[rule_id] = new_rule
    
    return new_rule

@router.get("/{rule_id}", response_model=Rule)
async def get_rule(rule_id: str):
    """Get specific rule by ID"""
    if rule_id not in rules_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id '{rule_id}' not found"
        )
    
    return rules_db[rule_id]

@router.put("/{rule_id}", response_model=Rule)
async def update_rule(rule_id: str, rule_update: RuleUpdate):
    """
    Update rule including toggles
    
    Allows partial updates - only provided fields will be updated
    """
    if rule_id not in rules_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id '{rule_id}' not found"
        )
    
    existing_rule = rules_db[rule_id]
    
    # Update only provided fields
    update_data = rule_update.dict(exclude_unset=True)
    
    # Validation for content type changes
    if 'target_content_type' in update_data:
        content_type = update_data['target_content_type']
        valid_content_types = ['post', 'reel', 'story', 'all-content']
        if content_type not in valid_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type. Must be one of: {valid_content_types}"
            )
    
    # Update the rule
    for field, value in update_data.items():
        setattr(existing_rule, field, value)
    
    existing_rule.updated_at = datetime.utcnow().isoformat()
    
    return existing_rule

@router.patch("/{rule_id}/toggle", response_model=Rule)
async def toggle_rule_status(rule_id: str, toggle_data: RuleToggleStatus):
    """
    Toggle rule active/inactive status
    
    Quick endpoint for enabling/disabling rules
    """
    if rule_id not in rules_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id '{rule_id}' not found"
        )
    
    rule = rules_db[rule_id]
    rule.is_active = toggle_data.is_active
    rule.updated_at = datetime.utcnow().isoformat()
    
    return rule

@router.delete("/{rule_id}", status_code=status.HTTP_200_OK)
async def delete_rule(rule_id: str):
    """Delete rule permanently"""
    if rule_id not in rules_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id '{rule_id}' not found"
        )
    
    deleted_rule = rules_db.pop(rule_id)
    
    return {
        "message": "Rule deleted successfully",
        "deleted_rule": deleted_rule
    }

@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_rules(rule_ids: List[str]):
    """Delete multiple rules at once"""
    deleted = []
    not_found = []
    
    for rule_id in rule_ids:
        if rule_id in rules_db:
            deleted.append(rules_db.pop(rule_id))
        else:
            not_found.append(rule_id)
    
    return {
        "message": f"Deleted {len(deleted)} rule(s)",
        "deleted_count": len(deleted),
        "not_found_count": len(not_found),
        "not_found_ids": not_found
    }

@router.get("/stats/summary")
async def get_rules_stats():
    """Get summary statistics about rules"""
    rules = list(rules_db.values())
    
    active_rules = [r for r in rules if r.is_active]
    inactive_rules = [r for r in rules if not r.is_active]
    
    # Count by content type
    content_type_counts = {}
    for rule in rules:
        content_type = rule.target_content_type
        content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
    
    # Count by account
    account_counts = {}
    for rule in rules:
        account = rule.target_account
        account_counts[account] = account_counts.get(account, 0) + 1
    
    return {
        "total_rules": len(rules),
        "active_rules": len(active_rules),
        "inactive_rules": len(inactive_rules),
        "by_content_type": content_type_counts,
        "by_account": account_counts
    }