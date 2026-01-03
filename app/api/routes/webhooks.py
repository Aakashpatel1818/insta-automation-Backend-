"""Webhook routes for Instagram events"""

from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings
import logging

router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)

@router.get("/instagram")
async def verify_webhook(request: Request):
    """
    Verify webhook subscription
    Required by Meta for webhook verification
    """
    mode = request.query_params.get("hub.mode")
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"Webhook verification: mode={mode}, verify_token={verify_token[:10]}...")
    
    if mode == "subscribe" and verify_token == settings.INSTAGRAM_WEBHOOK_VERIFY_TOKEN:
        return int(challenge)  # Return challenge as plain text
    else:
        raise HTTPException(status_code=403, detail="Webhook verification failed")

@router.post("/instagram")
async def handle_webhook(request: Request):
    """
    Handle Instagram webhook events
    """
    try:
        data = await request.json()
        logger.info(f"Webhook received: {data}")
        
        # Verify it's an Instagram webhook
        if data.get("object") != "instagram":
            logger.warning(f"Non-Instagram webhook: {data.get('object')}")
            return {"status": "ok"}
        
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                # FIXED: Instagram uses "field", not "item"
                field = change.get("field")
                value = change.get("value", {})
                
                if field == "comments":
                    # Comment event
                    comment_text = value.get("text", "")
                    commenter_id = value.get("from", {}).get("id")
                    logger.info(f"📝 New comment: '{comment_text}' from {commenter_id}")
                    # TODO: Process comment with your automation rules
                    
                elif field == "messages":
                    # DM event
                    sender_id = value.get("from", {}).get("id")
                    sender_username = value.get("from", {}).get("username")
                    message_text = value.get("message", {}).get("text", "")
                    logger.info(f"💬 DM from @{sender_username} ({sender_id}): '{message_text}'")
                    # TODO: Process DM with your automation rules
                
                elif field == "mentions":
                    # Mention event
                    logger.info(f"🔖 Mention received: {value}")
                    # TODO: Handle mentions
                
        return {"status": "EVENT_RECEIVED"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
