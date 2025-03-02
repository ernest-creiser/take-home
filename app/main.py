import base64
import json
from typing import Any

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Payload(BaseModel):
    content: str


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
