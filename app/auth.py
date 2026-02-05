import os
import time
import requests
from jose import jwt
from jose.exceptions import JWTError

COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-2")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "us-east-2_qKGXKYWeq")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID", "36094ik5eiugklsp2rgoa8h97h")

ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

_jwks_cache = {"keys": None, "fetched_at": 0}


def _get_jwks():
    # Cache JWKS for 1 hour to avoid fetching every request
    now = time.time()
    if _jwks_cache["keys"] and (now - _jwks_cache["fetched_at"] < 3600):
        return _jwks_cache["keys"]

    resp = requests.get(JWKS_URL, timeout=10)
    resp.raise_for_status()
    _jwks_cache["keys"] = resp.json()["keys"]
    _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"]


def verify_cognito_jwt(token: str) -> dict:
    if not COGNITO_USER_POOL_ID:
        raise ValueError("COGNITO_USER_POOL_ID is not set")
    if not COGNITO_APP_CLIENT_ID:
        raise ValueError("COGNITO_APP_CLIENT_ID is not set")

    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        raise JWTError("Missing kid in token header")

    keys = _get_jwks()
    key = next((k for k in keys if k["kid"] == kid), None)
    if not key:
        raise JWTError("Public key not found for token")

    # Validate signature + issuer + audience
    claims = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        issuer=ISSUER,
        audience=COGNITO_APP_CLIENT_ID,
    )

    return claims
