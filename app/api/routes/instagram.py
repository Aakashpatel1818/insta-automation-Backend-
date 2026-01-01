import requests
from fastapi import APIRouter, HTTPException
from app.core.config import (
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_REDIRECT_URI
)

router = APIRouter(prefix="/instagram", tags=["Instagram"])


@router.post("/exchange-token")
def exchange_code_for_token(code: str):
    """
    Exchanges authorization code for Instagram access token
    """

    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"

    payload = {
        "client_id": INSTAGRAM_APP_ID,
        "client_secret": INSTAGRAM_APP_SECRET,
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "code": code,
    }

    response = requests.post(token_url, data=payload)
    data = response.json()

    if "access_token" not in data:
        raise HTTPException(status_code=400, detail=data)

    return {
        "access_token": data["access_token"],
        "expires_in": data.get("expires_in")
    }
