
import json
import os

def _response(status: int, body: dict):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }

def lambda_handler(event, context):
    # For HTTP API + JWT authorizer, claims live here:
    claims = (
        event.get("requestContext", {})
             .get("authorizer", {})
             .get("jwt", {})
             .get("claims", {})
    )
    sub = claims.get("sub")
    email = claims.get("email")

    path = event.get("rawPath", "/")
    if path == "/health":
        return _response(200, {"status": "ok"})
    if path == "/me":
        return _response(200, {"sub": sub, "email": email})

    return _response(404, {"error": "not found", "path": path})
