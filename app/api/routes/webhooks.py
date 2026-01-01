"""Webhook routes for Instagram events"""

from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings

router = APIRouter()

@router.get("/instagram")
async def verify_webhook(request: Request):
    """
    Verify webhook subscription
    Required by Meta for webhook verification
    """
    mode = request.query_params.get("hub.mode")
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and verify_token == settings.INSTAGRAM_WEBHOOK_VERIFY_TOKEN:
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Webhook verification failed")

@router.post("/instagram")
async def handle_webhook(request: Request):
    """
    Handle Instagram webhook events
    """
    data = await request.json()
    
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change["value"]
            
            # Check if this is a comment event
            if value.get("item") == "comment":
                # TODO: Process comment with toggle logic
                print(f"📝 Comment received: {value.get('comment_text')}")
            
            # Check if this is a DM event
            elif value.get("item") == "message":
                # TODO: Process DM
                print(f"💬 DM received from {value.get('from', {}).get('username')}")
    
    return {"status": "ok"}