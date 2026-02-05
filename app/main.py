import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose.exceptions import JWTError

from app.auth import verify_cognito_jwt

app = FastAPI()
security = HTTPBearer()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"git_sha": os.getenv("GIT_SHA", "unknown")}

def current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return verify_cognito_jwt(creds.credentials)
    except (JWTError, ValueError) as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/me")
def me(user: dict = Depends(current_user)):
    # 'sub' is the unique user id in Cognito
    return {"sub": user.get("sub"), "email": user.get("email")}
