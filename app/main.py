import base64
import hashlib
import hmac
import json
import os
from typing import Any, Literal

from fastapi import Body, FastAPI, Response
from pydantic import BaseModel

secret_key = os.getenv("SECRET_KEY", default="secret-key")

app = FastAPI()


def encode(msg: str) -> str:
    return base64.b64encode(msg.encode()).decode()


def decode(msg: str) -> str:
    return base64.b64decode(msg.encode()).decode()


@app.post("/encrypt")
def encrypt(payload: dict = Body()) -> dict[str, Any]:
    return {key: encode(json.dumps(val)) for key, val in payload.items()}


@app.post("/decrypt")
def decrypt(payload: dict = Body()) -> dict[str, Any]:
    return {key: json.loads(decode(val)) for key, val in payload.items()}


@app.post("/sign")
def sign(payload: Any = Body()) -> dict[Literal["signature"], str]:
    hm = hmac.new(
        secret_key.encode("utf-8"),
        json.dumps(payload).encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    return {"signature": hm.hexdigest()}


class VerifyPayload(BaseModel):
    signature: str
    data: Any


@app.post("/verify")
def verify(payload: VerifyPayload) -> dict:
    hm = hmac.new(
        secret_key.encode(), json.dumps(payload.data).encode(), digestmod=hashlib.sha256
    )
    if payload.signature == hm.hexdigest():
        return Response(status_code=204)
    else:
        return Response(status_code=422)
