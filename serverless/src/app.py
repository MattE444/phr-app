
import json
import os
import uuid
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.getenv("TABLE_NAME", "")
table = dynamodb.Table(TABLE_NAME)


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _response(status: int, body: dict):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def _claims(event) -> dict:
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )


def _user_pk(sub: str) -> str:
    return f"USER#{sub}"


def lambda_handler(event, context):
    path = event.get("rawPath", "/")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    # /health is already handled by API Gateway public route, but keeping it is fine too
    if path == "/health":
        return _response(200, {"status": "ok"})

    claims = _claims(event)
    sub = claims.get("sub")
    email = claims.get("email")

    if not sub:
        return _response(401, {"message": "Unauthorized"})

    # Identity endpoint
    if path == "/me" and method == "GET":
        return _response(200, {"sub": sub, "email": email})

    # ---- Providers ----
    if path == "/providers" and method == "POST":
        try:
            body = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return _response(400, {"error": "Invalid JSON body"})

        name = (body.get("name") or "").strip()
        if not name:
            return _response(400, {"error": "name is required"})

        provider_id = uuid.uuid4().hex[:8]
        item = {
            "pk": _user_pk(sub),
            "sk": f"PROVIDER#{provider_id}",
            "type": "provider",
            "providerId": provider_id,
            "name": name,
            "specialty": (body.get("specialty") or "").strip(),
            "phone": (body.get("phone") or "").strip(),
            "notes": (body.get("notes") or "").strip(),
            "createdAt": _now_iso(),
        }

        table.put_item(Item=item)
        return _response(201, {"provider": item})

    if path == "/providers" and method == "GET":
        resp = table.query(
            KeyConditionExpression=Key("pk").eq(_user_pk(sub)) & Key("sk").begins_with("PROVIDER#")
        )
        providers = resp.get("Items", [])
        return _response(200, {"providers": providers})

    return _response(404, {"error": "not found", "path": path, "method": method})
