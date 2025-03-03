from fastapi.testclient import TestClient
import pytest
import json

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "input,expected", [("app/payload.json", 200), ("app/payload-array.json", 422)]
)
def test_encrypt_200(input: str, expected: int):
    with open(input) as f:
        response = client.post("/encrypt", json=json.load(f))
    assert response.status_code == expected


@pytest.mark.parametrize("input", ["app/payload.json"])
def test_encrypt_decrypt(input: str):
    with open(input) as f:
        payload = json.load(f)

    response_encrypt = client.post("/encrypt", json=payload)
    encrypted_payload = response_encrypt.json()
    response_decrypt = client.post("/decrypt", json=encrypted_payload)

    assert response_decrypt.status_code == 200
    decrypted_payload = response_decrypt.json()
    assert len(decrypted_payload) == len(payload)
    assert all([v == payload[k] for k, v in decrypted_payload.items()])


@pytest.mark.parametrize("input", ["app/payload.json", "app/payload-array.json"])
def test_sign_and_verify(input: str):
    with open(input) as f:
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
