"""
Instagram API Routes
OAuth token exchange and Instagram Graph API integration
"""

import httpx
from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/instagram", tags=["Instagram"])


@router.post("/exchange-token")
async def exchange_code_for_token(code: str = Query(..., min_length=1)):
    """
    Exchange Instagram authorization code for access token.
    
    Handles OAuth flow step 2: exchange code for short-lived access token.
    
    Args:
        code (str): Authorization code from Instagram OAuth
        
    Returns:
        dict: {access_token, user_id, expires_in}
    """
    
    logger.info(f"Processing OAuth token exchange for code: {code[:10]}...")
    
    if not settings.instagram_configured:
        logger.error("Instagram API not configured")
        raise HTTPException(
            status_code=503,
            detail="Instagram API is not configured. Please check environment variables.",
        )
    
    token_url = f"{settings.get_instagram_base_url()}/oauth/access_token"
    
    payload = {
        "app_id": settings.INSTAGRAM_APP_ID,
        "app_secret": settings.INSTAGRAM_APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "code": code,
    }
    
    try:
        logger.debug(f"Sending OAuth token exchange request to {token_url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(token_url, data=payload)
        
        logger.debug(f"Instagram API response status: {response.status_code}")
        
    except httpx.TimeoutException:
        logger.error("Instagram API request timed out")
        raise HTTPException(
            status_code=504,
            detail="Instagram API request timed out. Please try again.",
        )
    except httpx.RequestError as e:
        logger.error(f"Instagram API request failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to Instagram API. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during token exchange",
        )
    
    try:
        data = response.json()
        logger.debug(f"Successfully parsed Instagram API response")
    except ValueError as e:
        logger.error(f"Failed to parse Instagram API response: {response.text}")
        raise HTTPException(
            status_code=502,
            detail="Invalid response format from Instagram API",
        )
    
    if "error" in data:
        error_message = data.get("error_description", data.get("error", "Unknown error"))
        logger.warning(f"Instagram API error: {error_message}")
        raise HTTPException(
            status_code=400,
            detail=error_message,
        )
    
    if "access_token" not in data:
        logger.error("Access token not in Instagram API response")
        raise HTTPException(
            status_code=502,
            detail="Instagram API did not return access token",
        )
    
    logger.info(f"Successfully exchanged code for access token (user: {data.get('user_id')})")
    
    return {
        "access_token": data["access_token"],
        "user_id": data.get("user_id"),
        "expires_in": data.get("expires_in"),
    }


@router.post("/refresh-token")
async def refresh_access_token(access_token: str = Query(..., min_length=1)):
    """
    Refresh short-lived access token to long-lived token.
    
    Instagram tokens expire. Use this to get a ~60 day token.
    
    Args:
        access_token (str): Short-lived token to refresh
        
    Returns:
        dict: {access_token, expires_in}
    """
    
    logger.info("Processing access token refresh")
    
    if not settings.instagram_configured:
        logger.error("Instagram API not configured")
        raise HTTPException(
            status_code=503,
            detail="Instagram API is not configured",
        )
    
    token_url = f"{settings.get_instagram_base_url()}/oauth/access_token"
    
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": access_token,
    }
    
    try:
        logger.debug(f"Sending token refresh request")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(token_url, params=params)
        
        logger.debug(f"Instagram API response status: {response.status_code}")
        
    except httpx.TimeoutException:
        logger.error("Token refresh request timed out")
        raise HTTPException(
            status_code=504,
            detail="Instagram API request timed out",
        )
    except httpx.RequestError as e:
        logger.error(f"Token refresh request failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to Instagram API",
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    
    try:
        data = response.json()
    except ValueError:
        logger.error(f"Failed to parse token refresh response: {response.text}")
        raise HTTPException(
            status_code=502,
            detail="Invalid response from Instagram API",
        )
    
    if "error" in data:
        error_message = data.get("error_description", data.get("error", "Unknown error"))
        logger.warning(f"Token refresh error: {error_message}")
        raise HTTPException(
            status_code=400,
            detail=error_message,
        )
    
    if "access_token" not in data:
        logger.error("Access token not in refresh response")
        raise HTTPException(
            status_code=502,
            detail="Failed to refresh access token",
        )
    
    logger.info("Successfully refreshed access token")
    
    return {
        "access_token": data["access_token"],
        "expires_in": data.get("expires_in"),
    }


@router.get("/validate-token")
async def validate_token(access_token: str = Query(..., min_length=1)):
    """
    Validate if an access token is still valid.
    
    Args:
        access_token (str): Token to validate
        
    Returns:
        dict: Token validity and info
    """
    
    logger.info("Validating Instagram access token")
    
    if not settings.instagram_configured:
        raise HTTPException(
            status_code=503,
            detail="Instagram API is not configured",
        )
    
    debug_url = f"{settings.get_instagram_base_url()}/debug_token"
    
    params = {
        "input_token": access_token,
        "access_token": access_token,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(debug_url, params=params)
        
        data = response.json()
        
        if "error" in data:
            logger.warning(f"Token validation failed: {data.get('error', {}).get('message')}")
            return {
                "valid": False,
                "error": data.get("error", {}).get("message", "Invalid token"),
            }
        
        token_data = data.get("data", {})
        is_valid = token_data.get("is_valid", False)
        
        logger.info(f"Token valid: {is_valid}")
        
        return {
            "valid": is_valid,
            "app_id": token_data.get("app_id"),
            "expires_at": token_data.get("expires_at"),
            "scopes": token_data.get("scopes", []),
        }
        
    except httpx.RequestError as e:
        logger.error(f"Token validation request failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="Failed to validate token",
        )
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def instagram_api_health():
    """
    Check if Instagram API is configured and accessible.
    
    Returns:
        dict: Configuration and connectivity status
    """
    
    logger.info("Checking Instagram API health")
    
    return {
        "status": "healthy" if settings.instagram_configured else "unconfigured",
        "configured": settings.instagram_configured,
        "api_version": settings.INSTAGRAM_API_VERSION,
        "has_credentials": bool(settings.INSTAGRAM_APP_ID),
        "message": (
            "Instagram API is properly configured" 
            if settings.instagram_configured 
            else "Instagram API credentials not configured"
        ),
    }