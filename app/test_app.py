from pathlib import Path
from fastapi.testclient import TestClient
import pytest
import json

from app.main import app

client = TestClient(app)


fixture_dir = Path("fixtures")


@pytest.mark.parametrize(
    "input,expected",
    [
        ("object.json", 200),
        ("empty-object.json", 200),
        ("array.json", 422),
        ("duplicate-key.json", 200),
    ],
)
def test_encrypt_200(input: str, expected: int):
    with open(fixture_dir / input) as f:
        response = client.post("/encrypt", json=json.load(f))
    assert response.status_code == expected


@pytest.mark.parametrize(
    "input", ["object.json", "empty-object.json", "emoji.json", "duplicate-key.json"]
)
def test_encrypt_decrypt(input: str):
    with open(fixture_dir / input) as f:
        payload = json.load(f)

    response_encrypt = client.post("/encrypt", json=payload)
    encrypted_payload = response_encrypt.json()
    response_decrypt = client.post("/decrypt", json=encrypted_payload)

    assert response_decrypt.status_code == 200
    decrypted_payload = response_decrypt.json()
    assert len(decrypted_payload) == len(payload)
    assert all([v == payload[k] for k, v in decrypted_payload.items()])


@pytest.mark.parametrize(
    "input",
    [
        "object.json",
        "array.json",
        "empty-object.json",
        "empty-array.json",
        "duplicate-key.json",
    ],
)
def test_sign_and_verify(input: str):
    with open(fixture_dir / input) as f:
        payload = json.load(f)

    response_sign = client.post("/sign", json=payload).json()
    response_verify = client.post(
        "/verify",
        json={
            "signature": response_sign["signature"],
            "data": payload,
        },
    )
    assert response_verify.status_code == 204
