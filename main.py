import json
from fastapi import FastAPI, HTTPException, Request
import requests
from fastapi.middleware.cors import CORSMiddleware

from constant import (
    AUTH_BASE_URL,
    CLEINT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    SCOPE,
    ACCESS_TYPE,
)
from datetime import UTC, datetime, timedelta

from router import router as zoho_router

app = FastAPI(title="Redirect API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.include_router(zoho_router)

@app.get("/redirect")
async def redirect():
    return {
        "url": f"{AUTH_BASE_URL}/oauth/v2/auth?scope={SCOPE}&client_id={CLEINT_ID}&response_type=code&access_type={ACCESS_TYPE}&redirect_uri={REDIRECT_URI}&prompt=consent"
    }


@app.get("/oauth")
async def oauth_callback(request: Request):
    """
    OAuth callback endpoint that receives the authorization code from Zoho.

    Query parameters:
    - code: Authorization code from Zoho (if successful)
    - error: Error message from Zoho (if authorization failed)
    """
    code = request.query_params.get("code")
    location = request.query_params.get("location")
    account_server = request.query_params.get("account-server")

    try:
        token_response = get_tokens(code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    access_token = token_response.get("access_token")
    refresh_token = token_response.get("refresh_token")
    expires_in = token_response.get("expires_in")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "location": location,
        "account_server": account_server,
        "expires_in": expires_in,
    }


def get_tokens(code: str):
    """
    Get access token from Zoho and save to response.json
    """
    url = f"{AUTH_BASE_URL}/oauth/v2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": code,
        "client_id": CLEINT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(
        url,
        headers=headers,
        data=data,
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )
    with open("response.json", "w") as f:
        data = response.json()
        expires_in = data.get("expires_in")
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        data["expires_at"] = expires_at.isoformat()
        f.write(json.dumps(data))
        return data