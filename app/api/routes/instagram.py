import requests
from fastapi import APIRouter, HTTPException
from app.core.config import (
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_REDIRECT_URI,
)

router = APIRouter(prefix="/instagram", tags=["Instagram"])


@router.post("/exchange-token")
def exchange_code_for_token(code: str):
    """
    Exchange Instagram authorization code for a short-lived access token.
    Expects `code` as a query parameter: /instagram/exchange-token?code=...
    """

    token_url = "https://api.instagram.com/oauth/access_token"

    payload = {
        "app_id": INSTAGRAM_APP_ID,
        "app_secret": INSTAGRAM_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "code": code,
    }

    try:
        response = requests.post(token_url, data=payload, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Instagram request failed: {e}")

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid response from Instagram: {response.text}",
        )

    if "access_token" not in data:
        # Forward Instagram error for easier debugging
        raise HTTPException(status_code=400, detail=data)

    return {
        "access_token": data["access_token"],
        "user_id": data.get("user_id"),
        "expires_in": data.get("expires_in"),
    }
