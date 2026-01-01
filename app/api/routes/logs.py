"""Logs and analytics routes - PRODUCTION READY with minimal changes"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime, timedelta
from enum import Enum
import logging

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# ENUMS FOR FILTERS
# ============================================================================

class DateFilter(str, Enum):
    ALL = "all"
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"


class StatusFilter(str, Enum):
    ALL = "all"
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"


class DMStatus(str, Enum):
    DELIVERED = "delivered"
    PENDING = "pending"
    FAILED = "failed"


# ============================================================================
# MODELS (Added validation, NO structural changes)
# ============================================================================

class CommentLog(BaseModel):
    """Comment activity log model"""
    id: str = Field(default="")
    timestamp: str
    post_url: str = Field(min_length=1, max_length=500)
    commenter_username: str = Field(min_length=1, max_length=100)
    commenter_user_id: str = Field(min_length=1, max_length=100)
    comment_text: str = Field(min_length=1, max_length=5000)
    reply_sent: bool
    reply_text: Optional[str] = Field(None, max_length=5000)
    rule_id: str = Field(min_length=1, max_length=100)
    rule_name: str = Field(min_length=1, max_length=200)
    target_account: str = Field(min_length=1, max_length=100)
    error_message: Optional[str] = Field(None, max_length=1000)

    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Invalid ISO format timestamp')


class DMLog(BaseModel):
    """DM activity log model"""
    id: str = Field(default="")
    sent_at: str
    recipient_username: str = Field(min_length=1, max_length=100)
    recipient_user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)
    status: DMStatus
    rule_id: str = Field(min_length=1, max_length=100)
    rule_name: str = Field(min_length=1, max_length=200)
    target_account: str = Field(min_length=1, max_length=100)
    error_message: Optional[str] = Field(None, max_length=1000)
    retry_count: int = Field(default=0, ge=0, le=10)

    @validator('sent_at')
    def validate_sent_at(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Invalid ISO format timestamp')


class Statistics(BaseModel):
    """Dashboard statistics"""
    total_comments: int
    total_dms_sent: int
    active_rules: int
    today_comments: int
    today_dms_sent: int
    week_comments: int
    week_dms_sent: int
    success_rate_comments: float
    success_rate_dms: float
    most_active_rule: Optional[str] = None
    most_active_account: Optional[str] = None


# ============================================================================
# IN-MEMORY STORAGE (UNCHANGED - Your pages need this)
# ============================================================================

comment_logs_db = {}
dm_logs_db = {}

# ============================================================================
# ALLOWED SORT FIELDS (Added for security - prevents injection)
# ============================================================================

ALLOWED_SORT_FIELDS_COMMENTS = {
    'timestamp', 'commenter_username', 'rule_name', 'target_account', 'reply_sent'
}

ALLOWED_SORT_FIELDS_DMS = {
    'sent_at', 'recipient_username', 'rule_name', 'target_account', 'status'
}


# ============================================================================
# HELPER FUNCTIONS (Fixed for robustness)
# ============================================================================

def validate_sort_by(sort_by: str, allowed_fields: set) -> str:
    """Validate sort_by parameter - SECURITY FIX"""
    if sort_by not in allowed_fields:
        # Default to first allowed field instead of crashing
        return list(allowed_fields)[0]
    return sort_by


def filter_by_date(logs: List, date_filter: DateFilter, timestamp_field: str = 'timestamp'):
    """Filter logs by date range - Added error handling"""
    try:
        if date_filter == DateFilter.ALL:
            return logs
        
        now = datetime.utcnow()
        if date_filter == DateFilter.TODAY:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == DateFilter.WEEK:
            start_date = now - timedelta(days=7)
        elif date_filter == DateFilter.MONTH:
            start_date = now - timedelta(days=30)
        else:
            return logs
        
        filtered = []
        for log in logs:
            try:
                log_date = datetime.fromisoformat(getattr(log, timestamp_field))
                if log_date >= start_date:
                    filtered.append(log)
            except (ValueError, AttributeError):
                # Skip logs with invalid timestamps
                continue
        
        return filtered
    except Exception as e:
        logger.error(f"Error filtering by date: {e}")
        return logs


def filter_by_status(logs: List, status_filter: StatusFilter, log_type: str = 'comment'):
    """Filter logs by status - UNCHANGED"""
    if status_filter == StatusFilter.ALL:
        return logs
    
    try:
        if log_type == 'comment':
            if status_filter == StatusFilter.SUCCESS:
                return [log for log in logs if log.reply_sent]
            elif status_filter == StatusFilter.PENDING:
                return [log for log in logs if not log.reply_sent and not log.error_message]
            elif status_filter == StatusFilter.FAILED:
                return [log for log in logs if log.error_message]
        else:  # DM logs
            return [log for log in logs if log.status == status_filter]
    except Exception as e:
        logger.error(f"Error filtering by status: {e}")
        return logs
    
    return logs


def search_logs(logs: List, search_query: Optional[str]):
    """Search logs by query - Added length limit"""
    if not search_query:
        return logs
    
    # SECURITY FIX: Limit search query length to prevent DoS
    if len(search_query) > 100:
        logger.warning(f"Search query too long: {len(search_query)} chars")
        return logs  # Return all logs if query too long
    
    try:
        query = search_query.lower()
        filtered = []
        
        for log in logs:
            # Convert log to dict and search in all string fields
            log_dict = log.dict() if hasattr(log, 'dict') else log.__dict__
            if any(query in str(value).lower() for value in log_dict.values()):
                filtered.append(log)
        
        return filtered
    except Exception as e:
        logger.error(f"Error searching logs: {e}")
        return logs


# ============================================================================
# ROUTES - COMMENTS (Fixed async, added error handling)
# ============================================================================

@router.get("/comments")
def get_comment_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_filter: DateFilter = Query(DateFilter.ALL),
    status_filter: StatusFilter = Query(StatusFilter.ALL),
    search: Optional[str] = Query(None, max_length=100),  # SECURITY: Added max_length
    account: Optional[str] = Query(None, max_length=100),  # SECURITY: Added max_length
    rule_id: Optional[str] = Query(None, max_length=100),  # SECURITY: Added max_length
    sort_by: str = Query("timestamp"),
    sort_order: Literal["asc", "desc"] = Query("desc")
):
    """
    Get comment activity logs with advanced filtering
    
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Number of records to return (max 100)
    - date_filter: Filter by date range (all, today, week, month)
    - status_filter: Filter by status (all, success, pending, failed)
    - search: Search query across all fields (max 100 chars)
    - account: Filter by target account
    - rule_id: Filter by specific rule
    - sort_by: Field to sort by
    - sort_order: Sort order (asc/desc)
    """
    try:
        # SECURITY FIX: Validate sort_by parameter
        sort_by = validate_sort_by(sort_by, ALLOWED_SORT_FIELDS_COMMENTS)
        
        # Get all logs
        logs = list(comment_logs_db.values())
        
        # Apply filters
        logs = filter_by_date(logs, date_filter, 'timestamp')
        logs = filter_by_status(logs, status_filter, 'comment')
        logs = search_logs(logs, search)
        
        # Filter by account
        if account:
            logs = [log for log in logs if log.target_account == account]
        
        # Filter by rule
        if rule_id:
            logs = [log for log in logs if log.rule_id == rule_id]
        
        # Sort logs - IMPROVED error handling
        reverse = sort_order == "desc"
        try:
            logs.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        except AttributeError:
            # Fallback to timestamp if field doesn't exist
            logs.sort(key=lambda x: x.timestamp, reverse=reverse)
        
        # Pagination
        total = len(logs)
        logs = logs[skip:skip + limit]
        
        logger.info(f"Retrieved {len(logs)} comment logs (total: {total})")
        
        return {
            "comments": logs,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        logger.error(f"Error retrieving comment logs: {e}")
        # Return empty result instead of crashing
        return {
            "comments": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "has_more": False,
            "error": str(e)
        }


# ============================================================================
# ROUTES - DMS (Fixed async, added error handling)
# ============================================================================

@router.get("/dms")
def get_dm_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_filter: DateFilter = Query(DateFilter.ALL),
    status_filter: StatusFilter = Query(StatusFilter.ALL),
    search: Optional[str] = Query(None, max_length=100),  # SECURITY: Added max_length
    account: Optional[str] = Query(None, max_length=100),  # SECURITY: Added max_length
    rule_id: Optional[str] = Query(None, max_length=100),  # SECURITY: Added max_length
    sort_by: str = Query("sent_at"),
    sort_order: Literal["asc", "desc"] = Query("desc")
):
    """
    Get DM activity logs with advanced filtering
    
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Number of records to return (max 100)
    - date_filter: Filter by date range (all, today, week, month)
    - status_filter: Filter by status (all, success, pending, failed)
    - search: Search query across all fields (max 100 chars)
    - account: Filter by target account
    - rule_id: Filter by specific rule
    - sort_by: Field to sort by
    - sort_order: Sort order (asc/desc)
    """
    try:
        # SECURITY FIX: Validate sort_by parameter
        sort_by = validate_sort_by(sort_by, ALLOWED_SORT_FIELDS_DMS)
        
        # Get all logs
        logs = list(dm_logs_db.values())
        
        # Apply filters
        logs = filter_by_date(logs, date_filter, 'sent_at')
        logs = filter_by_status(logs, status_filter, 'dm')
        logs = search_logs(logs, search)
        
        # Filter by account
        if account:
            logs = [log for log in logs if log.target_account == account]
        
        # Filter by rule
        if rule_id:
            logs = [log for log in logs if log.rule_id == rule_id]
        
        # Sort logs - IMPROVED error handling
        reverse = sort_order == "desc"
        try:
            logs.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        except AttributeError:
            # Fallback to sent_at if field doesn't exist
            logs.sort(key=lambda x: x.sent_at, reverse=reverse)
        
        # Pagination
        total = len(logs)
        logs = logs[skip:skip + limit]
        
        logger.info(f"Retrieved {len(logs)} DM logs (total: {total})")
        
        return {
            "dms": logs,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        logger.error(f"Error retrieving DM logs: {e}")
        # Return empty result instead of crashing
        return {
            "dms": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "has_more": False,
            "error": str(e)
        }


# ============================================================================
# ROUTES - STATISTICS (Fixed async, added error handling)
# ============================================================================

@router.get("/stats", response_model=Statistics)
def get_statistics():
    """
    Get comprehensive dashboard statistics
    
    Returns:
    - Total comments and DMs
    - Today's activity
    - Week's activity
    - Success rates
    - Most active rule and account
    """
    try:
        comment_logs = list(comment_logs_db.values())
        dm_logs = list(dm_logs_db.values())
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        
        # Total counts
        total_comments = len(comment_logs)
        total_dms_sent = len(dm_logs)
        
        # Today's activity
        today_comments = len([
            log for log in comment_logs 
            if datetime.fromisoformat(log.timestamp) >= today_start
        ])
        today_dms_sent = len([
            log for log in dm_logs 
            if datetime.fromisoformat(log.sent_at) >= today_start
        ])
        
        # Week's activity
        week_comments = len([
            log for log in comment_logs 
            if datetime.fromisoformat(log.timestamp) >= week_start
        ])
        week_dms_sent = len([
            log for log in dm_logs 
            if datetime.fromisoformat(log.sent_at) >= week_start
        ])
        
        # Success rates
        successful_comments = len([log for log in comment_logs if log.reply_sent])
        success_rate_comments = (successful_comments / total_comments * 100) if total_comments > 0 else 0
        
        successful_dms = len([log for log in dm_logs if log.status == DMStatus.DELIVERED])
        success_rate_dms = (successful_dms / total_dms_sent * 100) if total_dms_sent > 0 else 0
        
        # Most active rule
        rule_counts = {}
        for log in comment_logs + dm_logs:
            rule_name = log.rule_name
            rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1
        
        most_active_rule = max(rule_counts.items(), key=lambda x: x[1])[0] if rule_counts else None
        
        # Most active account
        account_counts = {}
        for log in comment_logs + dm_logs:
            account = log.target_account
            account_counts[account] = account_counts.get(account, 0) + 1
        
        most_active_account = max(account_counts.items(), key=lambda x: x[1])[0] if account_counts else None
        
        # Get active rules count (this should come from rules database)
        # For now, using unique rule names from logs
        active_rules = len(set(log.rule_name for log in comment_logs + dm_logs))
        
        logger.info("Retrieved dashboard statistics")
        
        return Statistics(
            total_comments=total_comments,
            total_dms_sent=total_dms_sent,
            active_rules=active_rules,
            today_comments=today_comments,
            today_dms_sent=today_dms_sent,
            week_comments=week_comments,
            week_dms_sent=week_dms_sent,
            success_rate_comments=round(success_rate_comments, 2),
            success_rate_dms=round(success_rate_dms, 2),
            most_active_rule=most_active_rule,
            most_active_account=most_active_account
        )
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        # Return zeros instead of crashing
        return Statistics(
            total_comments=0,
            total_dms_sent=0,
            active_rules=0,
            today_comments=0,
            today_dms_sent=0,
            week_comments=0,
            week_dms_sent=0,
            success_rate_comments=0.0,
            success_rate_dms=0.0,
            most_active_rule=None,
            most_active_account=None
        )


# ============================================================================
# ROUTES - DAILY STATS (Fixed async, added error handling)
# ============================================================================

@router.get("/stats/daily")
def get_daily_stats(days: int = Query(7, ge=1, le=90)):
    """
    Get daily statistics for charts/graphs
    
    Query Parameters:
    - days: Number of days to retrieve (default: 7, max: 90)
    
    Returns daily breakdown of comments and DMs
    """
    try:
        comment_logs = list(comment_logs_db.values())
        dm_logs = list(dm_logs_db.values())
        
        now = datetime.utcnow()
        daily_stats = []
        
        for i in range(days):
            date = now - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            day_comments = [
                log for log in comment_logs 
                if date_start <= datetime.fromisoformat(log.timestamp) < date_end
            ]
            day_dms = [
                log for log in dm_logs 
                if date_start <= datetime.fromisoformat(log.sent_at) < date_end
            ]
            
            daily_stats.append({
                "date": date_start.strftime("%Y-%m-%d"),
                "comments": len(day_comments),
                "dms": len(day_dms),
                "total": len(day_comments) + len(day_dms)
            })
        
        daily_stats.reverse()  # Oldest to newest
        
        logger.info(f"Retrieved {days} days of daily statistics")
        
        return {
            "daily_stats": daily_stats,
            "days": days
        }
    except Exception as e:
        logger.error(f"Error retrieving daily stats: {e}")
        return {
            "daily_stats": [],
            "days": days,
            "error": str(e)
        }


# ============================================================================
# ROUTES - BY RULE STATS (Fixed async, added error handling)
# ============================================================================

@router.get("/stats/by-rule")
def get_stats_by_rule():
    """Get statistics grouped by rule"""
    try:
        comment_logs = list(comment_logs_db.values())
        dm_logs = list(dm_logs_db.values())
        
        rule_stats = {}
        
        # Process comment logs
        for log in comment_logs:
            rule_name = log.rule_name
            if rule_name not in rule_stats:
                rule_stats[rule_name] = {
                    "rule_name": rule_name,
                    "rule_id": log.rule_id,
                    "total_comments": 0,
                    "successful_comments": 0,
                    "total_dms": 0,
                    "successful_dms": 0
                }
            
            rule_stats[rule_name]["total_comments"] += 1
            if log.reply_sent:
                rule_stats[rule_name]["successful_comments"] += 1
        
        # Process DM logs
        for log in dm_logs:
            rule_name = log.rule_name
            if rule_name not in rule_stats:
                rule_stats[rule_name] = {
                    "rule_name": rule_name,
                    "rule_id": log.rule_id,
                    "total_comments": 0,
                    "successful_comments": 0,
                    "total_dms": 0,
                    "successful_dms": 0
                }
            
            rule_stats[rule_name]["total_dms"] += 1
            if log.status == DMStatus.DELIVERED:
                rule_stats[rule_name]["successful_dms"] += 1
        
        # Calculate success rates
        for rule in rule_stats.values():
            rule["comment_success_rate"] = (
                rule["successful_comments"] / rule["total_comments"] * 100 
                if rule["total_comments"] > 0 else 0
            )
            rule["dm_success_rate"] = (
                rule["successful_dms"] / rule["total_dms"] * 100 
                if rule["total_dms"] > 0 else 0
            )
        
        logger.info(f"Retrieved stats for {len(rule_stats)} rules")
        
        return {
            "rule_stats": list(rule_stats.values()),
            "total_rules": len(rule_stats)
        }
    except Exception as e:
        logger.error(f"Error retrieving rule statistics: {e}")
        return {
            "rule_stats": [],
            "total_rules": 0,
            "error": str(e)
        }


# ============================================================================
# ROUTES - CREATE LOGS (Fixed async, added validation)
# ============================================================================

@router.post("/comments")
def create_comment_log(log: CommentLog):
    """
    Create a new comment log entry (used by automation service)
    
    FIXED: Removed 'async', added validation via Pydantic
    """
    try:
        import uuid
        
        # Validate log (Pydantic will check all fields)
        if not log.timestamp:
            log.timestamp = datetime.utcnow().isoformat()
        
        log_id = str(uuid.uuid4())
        log.id = log_id
        
        comment_logs_db[log_id] = log
        
        logger.info(f"Created comment log: {log_id}")
        
        return {
            "message": "Comment log created",
            "id": log_id,
            "timestamp": log.timestamp
        }
    except Exception as e:
        logger.error(f"Error creating comment log: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid log data: {str(e)}")


@router.post("/dms")
def create_dm_log(log: DMLog):
    """
    Create a new DM log entry (used by automation service)
    
    FIXED: Removed 'async', added validation via Pydantic
    """
    try:
        import uuid
        
        # Validate log (Pydantic will check all fields)
        if not log.sent_at:
            log.sent_at = datetime.utcnow().isoformat()
        
        log_id = str(uuid.uuid4())
        log.id = log_id
        
        dm_logs_db[log_id] = log
        
        logger.info(f"Created DM log: {log_id}")
        
        return {
            "message": "DM log created",
            "id": log_id,
            "sent_at": log.sent_at
        }
    except Exception as e:
        logger.error(f"Error creating DM log: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid log data: {str(e)}")


# ============================================================================
# ROUTES - DELETE LOGS (Fixed async)
# ============================================================================

@router.delete("/comments/{log_id}")
def delete_comment_log(log_id: str):
    """Delete a comment log entry"""
    try:
        if log_id not in comment_logs_db:
            raise HTTPException(status_code=404, detail="Comment log not found")
        
        del comment_logs_db[log_id]
        
        logger.info(f"Deleted comment log: {log_id}")
        
        return {"message": "Comment log deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment log: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete log")


@router.delete("/dms/{log_id}")
def delete_dm_log(log_id: str):
    """Delete a DM log entry"""
    try:
        if log_id not in dm_logs_db:
            raise HTTPException(status_code=404, detail="DM log not found")
        
        del dm_logs_db[log_id]
        
        logger.info(f"Deleted DM log: {log_id}")
        
        return {"message": "DM log deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting DM log: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete log")


# ============================================================================
# ROUTES - MAINTENANCE (Fixed async)
# ============================================================================

@router.post("/clear")
def clear_all_logs(log_type: Optional[Literal["comments", "dms", "all"]] = "all"):
    """
    Clear all logs (use with caution!)
    
    FIXED: Removed 'async' keyword
    """
    try:
        if log_type in ["comments", "all"]:
            comment_logs_db.clear()
            logger.warning("Cleared all comment logs")
        
        if log_type in ["dms", "all"]:
            dm_logs_db.clear()
            logger.warning("Cleared all DM logs")
        
        return {
            "message": f"Cleared {log_type} logs successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear logs")